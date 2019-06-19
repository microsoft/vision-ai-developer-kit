# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

"""
This module provides iterator for getting frame and inference.
"""

import json
#import numpy as np
import subprocess
import time
from itertools import repeat

class CameraInference(object):
    """
    This is a class for inferences obtained from the camera.

    Attributes
    ----------
    timestamp : int
        Timestamp at which the inferences where made by the camera.
    objects : list of CameraInferenceObject objects
        List of inferences obtained from the camera.

    """
    def __init__(self, timestamp, objects):
        """
        This is the constructor for the CameraInference class.

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
    position : object of CameraInferenceObjectPosition type
        Position of the identified object.

    """
    def __init__(self, id, label, confidence, position=None):
        """
        This is the constructor for CameraInferenceObject class.

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
        width of the inferenced object from x.
    height : int
        height of the inferenced object from y.

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

    """
    def __init__(self):
        """
        This is the constructor for VideoInferenceIterator class.

        """
        #: str: Holds the JSON inference metadata obtained from the camera
        self._json_str = ""
        #: subprocess: object where gstreamer pipeline for capture inference
        #:             stream is run.
        self._sub_proc = None

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
            An object of CameraInference type.
            Which has timestamp and list of CameraInferenceObject objects.

        """
        cmd = ['gst-launch-1.0 ', ' -q ', ' rtspsrc ', ' location=' + result_src, ' protocols=tcp ',
               ' ! ', " application/x-rtp, media=application ", ' ! ', ' fakesink ', ' dump=true ']
        cmd = ''.join(cmd)
        #cmd = "gst-launch-1.0 -q rtspsrc location=rtsp://192.168.1.84:8902/live protocols=tcp ! application/x-rtp, media=application ! fakesink dump=true "
        print(cmd)
        try:
            self._sub_proc = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=False)
            #for x in range(10000):
            for _ in repeat(None):
                line = self._sub_proc.stdout.readline()
                #print("entered!!")
                l_str = line[70:-1]
                l_str = l_str.decode('utf-8')
                l_str = l_str.strip()
                #print(l_str)
                if ":[" in self._json_str and "] }" in self._json_str + l_str:
                    # Only yield if objects are present in the inferences
                    self._json_str = self._json_str + l_str
                    s_idx = self._json_str.index('{ "')
                    e_idx = self._json_str.index("] }") + 3
                    self._json_str = self._json_str[s_idx:e_idx]
                    #print(self._json_str)
                    result = self._get_inference_result()
                    self._json_str = ""
                    yield result
                elif ":[" not in self._json_str and '{ "' in self._json_str and " }" in self._json_str + 'l_str':
                    self._json_str = ""
                else:
                    self._json_str = self._json_str + l_str
                pass    
        except subprocess.CalledProcessError as e:
            print(e)

    def stop(self):
        """
        This method stops the inference generator.

        """
        if self._sub_proc:
            self._sub_proc.terminate()

    def _get_inference_result(self):
        """
        Private method for creating CameraInference object

        This method extracts the inference result from the
        VA json metadata string.

        Returns
        -------
        CameraInference
            CameraInference object with extracted values on success.
            CameraInference object with None if the json_str does not
            have any values or there is a malformed string.

        """
        try:
            j = json.loads(self._json_str)
            objects = []
            #print("reached!!!")
            for object in j["objects"]:
                #TODO preview resolution should be fetched from webserver
                #print("reachedloop!!!")
                x = (object["position"]["x"] * 1920) / 10000
                y = (object["position"]["y"] * 1080) / 10000
                w = (object["position"]["width"] * 1920) / 10000
                h = (object["position"]["height"] * 1080) / 10000
                position = CameraInferenceObjectPosition(x, y, w, h)
                result_object = CameraInferenceObject(
                    object["id"], object["display_name"], object["confidence"], position)
                objects.append(result_object)
            return CameraInference(j["timestamp"], objects)
        except ValueError as e:
            print(e)
            return CameraInference(None, None)
