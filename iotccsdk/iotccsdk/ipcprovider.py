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
This module provides APIs for communicating with QMMF IPC webserver.
"""

import requests
import json
import traceback
import logging
import threading
import websocket
import os


class IpcProvider():
    """
    This class provides interface to QMMF IPC webserver.

    Attributes
    ----------
    username : str
        username of the camera.
    password : str
        password of the camera.
    ip_address : str
        IP address of the camera.

    """

    def __init__(self, ip=None, username=None, password=None):
        """
        This is the constructor for `IpcProvider` class

        """
        self.username = username
        self.password = password
        self.ip_address = ip
        #: str: Port over which the camera/QMMF IPC webserver
        #:      communicates.
        self._port = '1080'
        #: str: Session identifier obtained from the
        #:      camera/QMMF IPC webserver .
        self._session_token = None
        self._heart_beat_manager = None
        self.logger = logging.getLogger('iotccsdk')

    def _show_error(self, err_msg):
        """
        Private method for logging error messages.

        Parameters
        ----------
        err_msg : str
            Error message to be logged.

        """
        self.logger.error(err_msg)

    def _get_function_name(self):
        """
        Private method for getting function name.

        Returns
        -------
            Function name from which it is called.

        """
        return traceback.extract_stack(None, 2)[0][2]

    def _build_url(self, path, params=None):
        """
        Private method for constructing request url.

        Returns
        -------
        str
            Constructed request url

        """
        return "http://" + self.ip_address + ":" + self._port + path

    def get(self, path, payload=None, param=None):
        """
        GET API for QMMF IPC webserver.

        Parameters
        ----------
        path : str
            QMMF IPC webserver API.
        payload : str
            JSON payload for the `path` API.
        param : str
            Params for the `path` API.

        Returns
        -------
        bool
            True if the GET was successful.
            False on failure.

        Raises
        ------
        Exception
            Any exception that occurs during the request.

        """
        try:
            with requests.session() as mysession:

                url = self._build_url(path)
                payload_data = json.dumps(payload)
                self.logger.info("API: " + url + ",data:" + payload_data)
                headers = {'Cookie': self._session_token}
                if not param:
                    response = mysession.get(
                        url, data=payload_data, headers=headers)
                else:
                    response = mysession.get(
                        url, data=payload_data, param=param, headers=headers)

                self.logger.info("RESPONSE: " + response.text)

                result = json.loads(response.text)
                return result
            return False
        except Exception as e:
            self.logger.exception(e)
            raise

    def post(self, path, payload=None, param=None):
        """
        POST API for QMMF IPC webserver.

        Parameters
        ----------
        path : str
            QMMF IPC webserver API.
        payload : str
            JSON payload for the `path` API.
        param : str
            Params for the `path` API.

        Returns
        -------
        bool
            True if the GET was successful.
            False on failure.

        Raises
        ------
        Exception
            Any exception that occurs during the request.

        """
        try:
            with requests.session() as mysession:
                url = self._build_url(path)
                payload_data = json.dumps(payload)
                self.logger.info("API: " + url + ",data:" + payload_data)
                headers = {'Cookie': self._session_token}
                if not param:
                    response = mysession.post(
                        url, data=payload_data, headers=headers)
                else:
                    response = mysession.post(
                        url, data=payload_data, param=param, headers=headers)

                self.logger.info("RESPONSE: " + response.text)

                result = json.loads(response.text)
                return result
            return False
        except Exception as e:
            self.logger.exception(e)
            raise

    def connect(self):
        """
        Establish a connection with QMMF IPC webserver on the camera.

        This API also sets the `session_token` attribute from the token
        obtained from the camera.

        Returns
        -------
        bool
            True if the connection was successful.
            False on failure.

        Raises
        ------
        Timeout
            When the request times out on the connect request.
        RequestException
            The request is not correctly formed.

        """
        if self._session_token:
            # This is to clear out previous session before starting a new one
            self.logout()

        with requests.session() as mysession:
            try:
                payload = "{\"username\": \"%s\", \"userpwd\": \"%s\"}" % (
                    self.username, self.password)
                host = self.ip_address + ":" + self._port
                url = "http://" + host + "/login"
                self.logger.info("API: " + url + ",data: " +
                                 json.dumps(payload, sort_keys=True))
                response = mysession.post(url, data=payload)
                self.logger.info("LOGIN RESPONSE: " + response.text)
                json_resp = json.loads(response.text)
                if json_resp['status']:
                    self._session_token = response.headers['Set-Cookie']
                    self.logger.debug(
                        "connection established with session token: [%s]" % self._session_token)
                    self._heart_beat_manager = HeartBeatManager(
                        host, self._session_token)
                    return True
                else:
                    raise requests.ConnectionError(
                        "Failed to connect. Server returned status=False")

            except requests.exceptions.Timeout:
                # TODO: user should have a way to figure out if required services are running?
                # maybe some simple URL
                self.logger.error(
                    "Timeout: Please check the device is running and the IPC service is available")
                raise
            except requests.exceptions.RequestException as e:
                self.logger.exception(e.strerror)
                raise
            except Exception as e:
                self.logger.exception(e)
                raise

    def logout(self):
        """
        Logout from the QMMF IPC webserver on the camera.

        Returns
        -------
        bool
            True if the logout was successful.
            False on failure.

        Raises
        ------
        Exception
            Any exception that occurs during the request.

        """
        try:
            if self._heart_beat_manager:
                self._heart_beat_manager.stop()
            path = "/logout"
            response = self.post(path)
            return response["status"]
        except Exception as e:
            self.logger.exception(e)
            raise


class HeartBeatManager():
    def __init__(self, host=None, cookie=None):
        self.logger = logging.getLogger('iotccsdk')
        websocket.enableTrace(True)
        uri = 'ws://' + host + '/async'
        self.logger.info("Connecting to: " + uri)
        self._ws = websocket.WebSocketApp(uri,
                                          on_message=lambda ws, msg: self.on_message(
                                              ws, msg),
                                          on_error=lambda ws, msg: self.on_error(
                                              ws, msg),
                                          on_close=lambda ws: self.stop,
                                          on_open=lambda ws: self.on_open(ws))
        t = threading.Thread(target=self.run)
        t.start()

    def on_message(self, ws, message):
        self.logger.debug(message)

    def on_error(self, ws, error):
        self.logger.error("Camera Restarted! Exiting!!")
        # raise Exception ("Camera Restarted! Exiting!!")
        os._exit(-1)

    def on_open(self, ws):
        self.logger.info("Starting heartbeat...")

    def run(self):
        self._ws.run_forever(ping_interval=11, ping_timeout=10)

    def stop(self):
        self.logger.info("Stoping heartbeat...")
        if self._ws:
            self._ws.close()
