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
This module contains the high level client APIs.

"""

import base64
import logging
import os
import sys
import time
from contextlib import contextmanager
from ipcprovider import IpcProvider
from frame_iterators import VideoInferenceIterator

class CameraClient():
    """
    This is a class for high level client APIs.

    Attributes
    ----------
    ipc_provider : IpcProvider object
    preview_running : bool
        Flag for preview status.
    preview_url : str
    vam_running : bool
        Flag for vam status.
    vam_url : str
    resolutions : list of str
        List of supported resolutions values.
        Use this for `configure_preview` API.
    encodetype : list of str
        List of supported codec types.
        Use this for `configure_preview` API.
    bitrates : list of str
        List of supported bitrates values.
        Use this for `configure_preview` API.
    framerates : list of int
        List of supported fps values.
        Use this for `configure_preview` API.
    cur_resolution: str
        Current preview resolution
    cur_codec: str
        Current preview encode type
    cur_bitrate: str
        Current preview bitrate
    cur_framerate: int
        Current preview framerate
    display_out: int
        Flag that tells whether HDMI display/preview is enabled or not.
        HDMI display/preview is enabled if this flag is 1 else disabled.
        This can be configured using `configure_preview` API.
    """
    logger = logging.getLogger('iotccsdk')

    @classmethod
    @contextmanager
    def connect(self, ipc_provider=None, ip_address=None, username=None, password=None):
        """
        This method is used to create CameraClient handle for application.

        Parameters
        ----------
        ipc_provider : `IpcProvider` object
            `IpcProvider` handle for class methods.
        ip_address : str
            IP address of the camera.
        username : str
            username for the camera.
        password : str
            password for the camera.

        Yields
        ------
        CameraClient
            `CameraClient` handle for the application.

        """
        if ipc_provider is None:
            ipc_provider = IpcProvider(ip = ip_address, username = username, password = password)

        ipc_provider.connect()
        try:
            yield CameraClient(ipc_provider)
        except Exception as e:
            self.logger.exception(e)
            raise
        finally:
            ipc_provider.logout()

    def __init__(self, ipc_provider):
        """
        The constructor for `CameraClient` class

        Parameters
        ----------
        ipc_provider : `IpcProvider` object

        """
        self.ipc_provider = ipc_provider
        self.preview_running = False
        self.preview_url = ""
        self.vam_running = False
        self.vam_url = ""
        self.record_running = False
        self.resolutions = []
        self.encodetype = []
        self.bitrates = []
        self.framerates = []
        self.cur_resolution = ""
        self.cur_codec = ""
        self.cur_bitrate = ""
        self.cur_framerate = 0
        self.display_out = 0
        self._get_supported_params()

    @contextmanager
    def get_inferences(self):
        """
        Inference generator for the application.

        This inference generator gives inferences from the VA metadata stream.

        Yields
        ------
        AiCameraInference: `AiCameraInference` class object
            This `AiCameraInference` object yielded
            from `VideoInferenceIterator.start()`

        Raises
        ------
        EOFError
            If the preview is not started.
            Or if the vam is not started.

        """
        if not self.preview_running:
            raise EOFError("preview not started")

        if not self.vam_running:
            raise EOFError("VAM not started")

        if self.cur_resolution == "4K":
            preview_width = 3840
            preview_height = 2160
        elif self.cur_resolution == "1080P":
            preview_width = 1920
            preview_height = 1080
        elif self.cur_resolution == "720P":
            preview_width = 1280
            preview_height = 720
        elif self.cur_resolution == "480P":
            preview_width = 640
            preview_height = 480

        inference_iterator = VideoInferenceIterator(preview_width, preview_height)

        try:
            if self.vam_url == "":
                self._get_vam_info()
            if "0.0.0.0" in self.vam_url:
                s_idx = self.vam_url.index('0')
                start = self.vam_url[:s_idx]
                e_idx = s_idx + len("0.0.0.0")
                end = self.vam_url[e_idx:]
                self.vam_url = start + "127.0.0.1" + end
            yield inference_iterator.start(self.vam_url)
        except Exception as e:
            self.logger.exception(e)
            raise
        finally:
            inference_iterator.stop()

    @contextmanager
    def configure_preview(self, resolution=None, encode=None, bitrate=None, framerate=None, display_out=None):
        """
        This method is for setting preview params.

        Parameters
        ----------
        resolution : str
            A value from `resolutions` attribute
        encode : str
            A value from `encodetype` attribute
        bitrate : str
            A value from `bitrates` attribute
        framerate : int
            A value from `framerates` attribute
        display_out : {0, 1}
            For enabling or disabling HDMI output

        Returns
        -------
        bool
            True if the request is successful. False on failure.

        """
        if resolution and self.resolutions and resolution in self.resolutions:
            res = self.resolutions.index(resolution)
        else:
            res = self.resolutions.index(self.cur_resolution)
        if encode and self.encodetype and encode in self.encodetype:
            enc = self.encodetype.index(encode)
        else:
            enc = self.encodetype.index(self.cur_codec)
        if bitrate and self.bitrates and bitrate in self.bitrates:
            bit = self.bitrates.index(bitrate)
        else:
            bit = self.bitrates.index(self.cur_bitrate)
        if framerate and self.framerates and framerate in self.framerates:
            fps = self.framerates.index(framerate)
        else:
            fps = self.framerates.index(self.cur_framerate)

        if display_out is None or (display_out > 1 and display_out < 0):
            self.logger.error("Invalid value: display_out should 0/1, using current display_out:{}".format(self.display_out))
            display_out = self.display_out

        path = "/video"
        payload = {
            "resolutionSelectVal": res,
            "encodeModeSelectVal": enc,
            "bitRateSelectVal": bit,
            "fpsSelectVal": fps,
            "displayOut": display_out
        }
        response = self.ipc_provider.post(path, payload)
        if response["status"]:
            if self.cur_resolution != self.resolutions[res]:
                self.cur_resolution = self.resolutions[res]
                self.logger.info('resolution updated to : ' + self.cur_resolution)
            if self.cur_codec != self.encodetype[enc]:
                self.cur_codec = self.encodetype[enc]
                self.logger.info('encodetype updated to : ' + self.cur_codec)
            if self.cur_bitrate != self.bitrates[bit]:
                self.cur_bitrate = self.bitrates[bit]
                self.logger.info('bitrate updated to : ' + self.cur_bitrate)
            if self.cur_framerate != self.framerates[fps]:
                self.cur_framerate = self.framerates[fps]
                self.logger.info('framerate updated to : {}'.format(self.cur_framerate))
            if self.display_out != display_out:
                self.display_out = display_out
                self.logger.info('display_out updated to : {}'.format(self.display_out))
        return response["status"]

    def _get_supported_params(self):
        """
        Private method for getting preview params

        This method populates the `resolutions`, `encodetype`, `bitrates`
        and `framerates` attribute. It is called by the `CameraClient` constructor.

        Returns
        -------
        bool
            True if the request is successful. False on failure.

        """
        path = "/video"
        payload = '{ }'
        response = self.ipc_provider.get(path, payload)
        if response["status"]:
            self.resolutions = response["resolution"]
            r_idx = response["resolutionSelectVal"]
            self.cur_resolution = self.resolutions[r_idx]
            self.encodetype = response["encodeMode"]
            e_idx = response["encodeModeSelectVal"]
            self.cur_codec = self.encodetype[e_idx]
            self.bitrates = response["bitRate"]
            b_idx = response["bitRateSelectVal"]
            self.cur_bitrate = self.bitrates[b_idx]
            self.framerates = response["fps"]
            f_idx = response["fpsSelectVal"]
            self.cur_framerate = self.framerates[f_idx]
            self.display_out = response["displayOut"]
            self.logger.info('resolutions: ' + str(self.resolutions))
            self.logger.info('encodetype: ' + str(self.encodetype))
            self.logger.info('bitrates: ' + str(self.bitrates))
            self.logger.info('framerates: ' + str(self.framerates))
            self.logger.info('Current preview settings:')
            self.logger.info('resolution: ' + self.cur_resolution)
            self.logger.info('encodetype: ' + self.cur_codec)
            self.logger.info('bitrate: ' + self.cur_bitrate)
            self.logger.info('framerate: {} '.format(self.cur_framerate))
            self.logger.info('display_out: {}'.format(self.display_out))

        return response["status"]

    @contextmanager
    def set_preview_state(self, state):
        """
        This is a switch for preview.

        Preview can be enabled or disabled using this API.

        Parameters
        ----------
        state : str
            Set it "on" for enabling or "off" for disabling preview.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        if state.lower() == "on":
            status = True
        elif state.lower() == "off":
            status = False
        else:
            self.logger.error("Invalid state: " + state + " should be on/off")
        path = "/preview"
        payload = {'switchStatus' : status}
        response = self.ipc_provider.post(path, payload)
        self.preview_running = response["status"]
        if status and self.preview_running:
            self._get_preview_info()
        return self.preview_running

    @contextmanager
    def _get_preview_info(self):
        """
        Private method for getting preview url

        Returns
        -------
        str
            Preview RTSP url

        """
        path = "/preview"
        payload = '{ }'
        response = self.ipc_provider.get(path, payload)
        self.preview_url = response["url"]
        self.logger.info('preview url: ' + self.preview_url)
        return self.preview_url

    @contextmanager
    def set_analytics_state(self, state):
        """
        This is a switch for video analytics(VA).

        VA can be enabled or disabled using this API.

        Parameters
        ----------
        state : str
            Set it "on" for enabling or "off" for disabling Video Analytics.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        if state.lower() == "on":
            status = True
        elif state.lower() == "off":
            status = False
        else:
            self.logger.error("Invalid state: " + state + " should be on/off")
        payload = {"switchStatus": status, "vamconfig": "MD"}
        path = "/vam"
        response = self.ipc_provider.post(path, payload)
        self.vam_running = response["status"]
        if status and self.vam_running:
            self._get_vam_info()
        return self.vam_running

    @contextmanager
    def _get_vam_info(self):
        """
        Private method for getting VA url

        Returns
        -------
        str
            Preview VA url

        """
        path = "/vam"
        payload = '{ }'
        response = self.ipc_provider.get(path, payload)
        self.vam_url = response["url"]
        self.logger.info('vam url: ' + self.preview_url)
        return self.vam_url

    @contextmanager
    def set_recording_state(self, state):
        """
        This is a switch for recording.

        Recording can be enabled or disabled using this API.

        Parameters
        ----------
        state : str
            Set it "on" for enabling or "off" for disabling recording.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        if state.lower() == "on":
            status = True
        elif state.lower() == "off":
            status = False
        else:
            self.logger.error("Invalid state: " + state + " should be on/off")
        path = "/recording"
        payload = {'switchStatus': status}
        response = self.ipc_provider.post(path, payload)
        self.record_running = response["status"]
        return self.record_running

    @contextmanager
    def configure_overlay(self, type=None, text=None):
        """
        This is for configuring overlay params.

        Parameters
        ----------
        type : {None, "inference", "text"}
            Type of the overlay you want to configure.
        text : str, optional
            Text for text overlay type (the default is None).

        Returns
            True if the configuration was successful.
            False on failure.

        """
        if type == "inference":
            return self._configure_inference_overlay()
        elif type == "text":
            return self._configure_text_overlay(text)
        else:
            self.logger.error("Invalid overlay type use (inference/text)")

    def _configure_inference_overlay(self):
        """
        Private method for inference overlay configuration.

        This is used by `configure_overlay` for inference type overlay.

        Returns
        -------
        bool
            True if the configuration was successful.
            False on failure.

        """
        path = "/overlayconfig"
        payload = {
            "ov_type_SelectVal": 5,
            "ov_position_SelectVal": 0,
            "ov_color": "869007615",
            "ov_usertext": "Text",
            "ov_start_x": 0,
            "ov_start_y": 0,
            "ov_width": 0,
            "ov_height": 0
        }
        response = self.ipc_provider.post(path, payload)
        return response["status"]

    def _configure_text_overlay(self, text):
        """
        Private method for text overlay configuration.

        This is used by `configure_overlay` for text type overlay.

        Returns
        -------
        bool
            True if the configuration was successful.
            False on failure.

        """
        path = "/overlayconfig"
        payload = {
            "ov_type_SelectVal": 0,
            "ov_position_SelectVal": 0,
            "ov_color": "869007615",
            "ov_usertext": text,
            "ov_start_x": 0,
            "ov_start_y": 0,
            "ov_width": 0,
            "ov_height": 0
        }
        response = self.ipc_provider.post(path, payload)
        return response["status"]

    @contextmanager
    def set_overlay_state(self, state=None):
        """
        This is a switch for overlay.

        Overlay can be enabled or disabled using this API.

        Parameters
        ----------
        state : str
            Set it "on" for enabling or "off" for disabling overlay.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        if state.lower() == "on":
            status = True
        elif state.lower() == "off":
            status = False
        else:
            self.logger.error("Invalid state: " + state + " should be on/off")
        path = "/overlay"
        payload = {"switchStatus": status}
        response = self.ipc_provider.post(path, payload)
        return response["status"]

    @contextmanager
    def captureimage(self):
        """
        This method is for taking a snapshot.

        The snapshot is taken and stored as snapshot_<timestamp>.jpg
        when the call is successful.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        path = "/captureimage"
        payload = '{ }'
        response = self.ipc_provider.post(path,payload)
        if response["Error"] != "none":
            self.logger.error(response["Error"])
            return False

        file_name = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'snapshot_' + str(response["Timestamp"])+ '.jpg')
        self.logger.info("Storing snapshot: {}".format(file_name))
        with open(file_name,"wb") as f:
            f.write(base64.b64decode(response["Data"]))
        return True
    @contextmanager
    def captureImageWithFolder(self, folder, tag1):
        """
        This method is for taking a snapshot.

        The snapshot is taken and stored as snapshot_<timestamp>.jpg
        when the call is successful.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        path = "/captureimage"
        payload = '{ }'
        response = self.ipc_provider.post(path, payload)
        if response["Error"] != "none":
            self.logger.error(response["Error"])
            return False
        picture_folder = os.path.join(os.path.dirname(os.path.abspath(__name__)), folder)
        if not os.path.exists(picture_folder):
            os.makedirs(picture_folder)
        tag_folder = os.path.join(os.path.dirname(os.path.abspath(__name__)), folder, tag1)
        if not os.path.exists(tag_folder):
            os.makedirs(tag_folder)
        file_name = os.path.join(tag_folder, tag1 + str(response["Timestamp"])+ '.jpg')
        self.logger.info("Storing snapshot: {}".format(file_name))
        with open(file_name,"wb") as f:
            f.write(base64.b64decode(response["Data"]))
        return True    
    @contextmanager
    def logout(self):
        """
        This method is for logging out from the camera.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        path = "/logout"
        response = self.ipc_provider.post(path)
        return response["status"]
