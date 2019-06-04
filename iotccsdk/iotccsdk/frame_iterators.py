# Copyright (c) 2018-2019, The Linux Foundation. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#    * Neither the name of The Linux Foundation nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This module provides iterator for getting frame and inference.
"""

import json
import logging
import os
import subprocess
import sys


class CameraInference(object):
    """
    This is a class for inferences obtained from the camera.

    Attributes
    ----------
    timestamp : int
        Timestamp at which the inferences where made by the camera.
    objects : list of `CameraInferenceObject` objects
        List of inferences obtained from the camera.

    """

    def __init__(self, timestamp, objects):
        """
        This is the constructor for the `CameraInference` class.

        """
        self.timestamp = timestamp
        self.objects = objects


class CameraInferenceObject(object):
    """
    This is a class for inference data obtained from the camera.

    Attributes
    ----------
    id : int
        ID of the identified object.
    label : str
        Label of the identified object.
    confidence : int
        Confidence value for the object in %.
    position : object of `CameraInferenceObjectPosition` type
        Position of the identified object.

    """

    def __init__(self, id, label, confidence, position=None):
        """
        This is the constructor for `CameraInferenceObject` class.

        """
        self.id = id
        self.label = label
        self.confidence = confidence
        self.position = position


class CameraInferenceObjectPosition(object):
    """
    This is a class for inferenced object position.

    Attributes
    ----------
    x : int
        x coordinate of the inferenced object.
    y : int
        y coordinate of the inferenced object.
    width : int
        width of the inferenced object from `x`.
    height : int
        height of the inferenced object from `y`.

    """

    def __init__(self, x, y, width, height):
        """
        This is the constructor for CameraInferenceObjectPosition class.

        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class VideoInferenceIterator(object):
    """
    This is a class for inference generator.

    Provides an generator method which can be used
    to get inferences from RTSP VA stream from
    the camera.

    Attributes
    ----------
    preview_width: int
        Preview stream width. This is required for object location
        calculation.
    preview_height: int
        Preview stream height. This is required for object location
        calculation.

    """

    def __init__(self, preview_width, preview_height):
        """
        This is the constructor for `VideoInferenceIterator` class.

        """
        self.preview_width = preview_width
        self.preview_height = preview_height
        #: str: Holds the JSON inference metadata obtained from the camera
        self._json_str = ""
        #: subprocess: object where gstreamer pipeline for capture inference
        #:             stream is run.
        self._sub_proc = None
        self.logger = logging.getLogger('iotccsdk')

    def start(self, result_src):
        """
        This is the inference generator method

        It gets inferences from the RTSP VA stream from the camera.

        Parameters
        ----------
        result_src : str
            VA RTSP stream url.

        Yields
        ------
        CameraInference
            An object of `CameraInference` type.
            Which has timestamp and list of `CameraInferenceObject` objects.

        Raises
        ------
        Exception
            Any exception that occurs during inference handling.

        """
        cmd = ['gst-launch-1.0 ',
               ' -q ',
               ' rtspsrc ',
               ' location=%s' % result_src,
               ' protocols=tcp ',
               ' ! ',
               ' application/x-rtp, media=application ',
               ' ! ',
               ' fakesink ',
               ' dump=true']
        cmd = ''.join(cmd)
        self.logger.info('result_src: %s' % result_src)
        self.logger.info('gstreamer cmd: %s' % str(cmd))
        platform = sys.platform
        platform = platform.lower()
        self.logger.info('Platform: %s' % platform)
        if 'win' in platform:
            data_idx = 78
        elif 'linux' in platform:
            data_idx = 72

        try:
            self._sub_proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, bufsize=1,
                                              universal_newlines=True)
            for line in self._sub_proc.stdout:
                if 'ERROR' in line or 'error' in line:
                    raise Exception(line)
                l_str = line[data_idx:]
                l_str = l_str.strip(os.linesep)
                self.logger.debug(l_str)
                if ":[" in self._json_str and "] }" in self._json_str + l_str:
                    # Only yield if objects are present in the inferences
                    self._json_str = self._json_str + l_str
                    s_idx = self._json_str.index('{ "')
                    e_idx = self._json_str.index("] }") + 3
                    self._json_str = self._json_str[s_idx:e_idx]
                    self.logger.debug(self._json_str)
                    result = self._get_inference_result()
                    self._json_str = ""
                    yield result
                elif (":[" not in self._json_str
                      and '{ "' in self._json_str
                      and " }" in self._json_str + l_str):
                    self._json_str = ""
                else:
                    self._json_str = self._json_str + l_str
        except (Exception, subprocess.CalledProcessError) as e:
            self.logger.exception(e)
            raise

    def stop(self):
        """
        This method stops the inference generator.

        """
        if self._sub_proc:
            self._sub_proc.terminate()

    def _get_inference_result(self):
        """
        Private method for creating `CameraInference` object

        This method extracts the inference result from the
        VA json metadata string.

        Returns
        -------
        CameraInference
            `CameraInference` object with extracted values on success.
            `CameraInference` object with None if the json_str does not
            have any values or there is a malformed string.

        """
        try:
            j = json.loads(self._json_str)
            objects = []
            for object in j["objects"]:
                x = (object["position"]["x"] * self.preview_width) / 10000
                y = (object["position"]["y"] * self.preview_height) / 10000
                w = (object["position"]["width"] * self.preview_width) / 10000
                h = (object["position"]["height"]
                     * self.preview_height) / 10000
                position = CameraInferenceObjectPosition(x, y, w, h)
                result_object = CameraInferenceObject(
                    object["id"], object["display_name"], object["confidence"], position)
                objects.append(result_object)
            return CameraInference(j["timestamp"], objects)
        except ValueError as e:
            self.logger.error(e)
            return CameraInference(None, None)
        except Exception as e:
            self.logger.exception(e)
            raise
