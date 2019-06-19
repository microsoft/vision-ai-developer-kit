# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

"""
This module contains the high level client APIs.

"""

import sys
from contextlib import contextmanager
from ipcprovider import IpcProvider
from frame_iterators import VideoInferenceIterator

class CameraClient():
    """
    This a class for high level client APIs.

    Attributes
    ----------
    connection : IpcProvider object
    preview_running : bool
        Flag for preview status.
    preview_url : str
    vam_running : bool
        Flag for vam status.
    vam_url : str
    resolutions : list of str
        List of supported resolutions values.
        Use this for configure_preview.
    encodetype : list of str
        List of supported codec types.
        Use this for configure_preview.
    bitrates : list of str
        List of supported bitrates values.
        Use this for configure_preview.
    framerates : list of int
        List of supported fps values.
        Use this for configure_preview.

    """
    @staticmethod
    @contextmanager
    def connect(connection=None, ip_address=None, username=None, password=None):
        """
        This method is used to create CameraClient handle for application.

        Parameters
        ----------
        connection : IpcProvider object
            IpcProvider handle for class methods.
        ip_address : str
            IP address of the camera.
        username : str
            username for the camera.
        password : str
            password for the camera.
        
        Yields
        ------
        CameraClient
            CameraClient handle for the application.

        """
        if connection is None:
            connection = IpcProvider(ip = ip_address, username = username, password = password)

        connection.connect()
        try:
            yield CameraClient(connection)
        finally:
            connection.logout()

    def __init__(self, connection):
        """
        The constructor for CameraClient class
        
        Parameters
        ----------
        connection : IpcProvider object

        """
        self.connection = connection
        self.preview_running = False
        self.preview_url = ""
        self.vam_running = False
        self.vam_url = ""
        self.resolutions = []
        self.encodetype = []
        self.bitrates = []
        self.framerates = []
        self._get_camera_params()

    @contextmanager
    def get_inferences(self, inference_iterator=None):
        """
        Inference generator for the application.

        This inference generator gives inferences from the VA metadata stream.

        Parameters
        ----------
        inference_iterator : VideoInferenceIterator class object

        Yields
        ------
        AiCameraInference: AiCameraInference class object
            This AiCameraInference object yielded
            from VideoInferenceIterator.start()

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

        if inference_iterator is None:
            inference_iterator = VideoInferenceIterator()
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
        finally:
            inference_iterator.stop()

    def _setup_model(self, model_config):
        # TODO: configure the common VAM here
        pass

    @contextmanager
    def configure_preview(self, resolution=None, encode=None, bitrate=None, framerate=None, display_out=None):
        """
        This method is for setting preview params.

        Parameters
        ----------
        resolution : str
            A value from resolutions attribute
        encode : str
            A value from encodetype attribute
        bitrate : str
            A value from bitrates attribute
        framerate : int
            A value from framerates attribute
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
            res = 1  # 1080P
        if encode and self.encodetype and encode in self.encodetype:
            enc = self.encodetype.index(encode)
        else:
            enc = 0  # HEVC
        if bitrate and self.bitrates and bitrate in self.bitrates:
            bit = self.bitrates.index(bitrate)
        else:
            bit = 6  # 4Mbps
        if framerate and self.framerates and framerate in self.framerates:
            fps = self.framerates.index(framerate)
        else:
            fps = 1  # 30

        if display_out > 1 and display_out < 0:
            print("Invalid value: display_out should 0/1, using default 0")
            display_out = 0

        path = "/video"
        payload = {
            "resolutionSelectVal": res,
            "encodeModeSelectVal": enc,
            "bitRateSelectVal": bit,
            "fpsSelectVal": fps,
            "displayOut": display_out
        }
        response = self.connection.post(path, payload)
        return response["status"]

    def _get_camera_params(self):
        """
        Private method for getting preview params

        This method populates the resolutions, encodetype, bitrates
        and framerates attribute. It is called by configure preview.

        Returns
        -------
        bool
            True if the request is successful. False on failure.

        """
        path = "/video"
        payload = '{ }'
        response = self.connection.get(path, payload)
        if response["status"]:
            self.resolutions = response["resolution"]
            self.encodetype = response["encodeMode"]
            self.bitrates = response["bitRate"]
            self.framerates = response["fps"]
        return response["status"]

    @contextmanager
    def toggle_preview(self, status):
        """
        This is a switch for preview.

        Preview can be enabled or disabled using this API.

        Parameters
        ----------
        status : bool
            Set it True for enabling and False for disabling preview.
        
        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        path = "/preview"
        payload = {'switchStatus' : status}
        response = self.connection.post(path, payload)
        self.preview_running = response["status"]
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
        response = self.connection.get(path, payload)
        if self.preview_running:
            self.preview_url = response["url"]
        return self.preview_url

    @contextmanager
    def toggle_vam(self, status):
        """
        This is a switch for VA.

        VA can be enabled or disabled using this API.

        Parameters
        ----------
        status : bool
            Set it True for enabling and False for disabling VA.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        payload = {"switchStatus": status, "vamconfig": "MD"}
        path = "/vam"
        response = self.connection.post(path, payload)
        self.vam_running = response["status"]
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
        response = self.connection.get(path, payload)
        if self.vam_running:
            self.vam_url = response["url"]
        return self.vam_url

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
            print("Invalid overlay type use (inference/text)")

    def _configure_inference_overlay(self):
        """
        Private method for inference overlay configuration.

        This is used by configure_overlay for inference type overlay.

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
        response = self.connection.post(path, payload)
        return response["status"]

    def _configure_text_overlay(self, text):
        """
        Private method for text overlay configuration.

        This is used by configure_overlay for text type overlay.

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
        response = self.connection.post(path, payload)
        return response["status"]

    @contextmanager
    def toggle_overlay(self, status=None):
        """
        This is a switch for overlay.

        Overlay can be enabled or disabled using this API.

        Parameters
        ----------
        status : bool
            Set it True for enabling and False for disabling overlay.

        Returns
        -------
        bool
            True if the request was successful. False on failure.

        """
        path = "/overlay"
        payload = {"switchStatus": status}
        response = self.connection.post(path, payload)
        return response["status"]

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
        response = self.connection.post(path)
        return response["status"]
