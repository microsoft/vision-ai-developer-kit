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
import sys
import logging

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

    def _build_url(self,path,params=None):
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
                if(param == None):
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
                if(param == None) :
                    response = mysession.post(url, data=payload_data, headers=headers)
                else :
                    response = mysession.post(url, data=payload_data, param=param, headers=headers)

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
        with requests.session() as mysession:
            try:
                payload = "{\"username\": \"%s\", \"userpwd\": \"%s\"}" % (self.username, self.password)
                url = "http://" + self.ip_address + ":" + self._port + "/login"
                self.logger.info("API: " + url + ",data: " + json.dumps(payload,sort_keys=True))
                response = mysession.post(url,data=payload)
                self.logger.info("LOGIN RESPONSE: " + response.text)
                json_resp = json.loads(response.text)
                if json_resp['status']:
                    self._session_token = response.headers['Set-Cookie']
                    self.logger.debug("connection established with session token: [%s]" % self._session_token)
                    return True
                else:
                    raise requests.ConnectionError(
                        "Failed to connect. Server returned status=False")

            except requests.exceptions.Timeout:
                # TODO: user should have a way to figure out if required services are running or not? maybe some simple URL
                self.logger.error(
                    "Timeout: Please check that the device is up and running and the IPC service is available")
                raise
            except requests.exceptions.RequestException as e:
                self.logger.exception(e.strerror)
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
            path =  "/logout"
            response = self.post(path)
            return response["status"]
        except Exception as e:
            self.logger.exception(e)
            raise
