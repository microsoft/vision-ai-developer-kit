# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

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
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.disabled = False

    def __init__(self, ip=None, username=None, password=None):
        """
        This is the constructor for IpcProvider class

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
            self.logger.error(e)
            self.logger.error('Exceptions raised in %s ',
                              self._get_function_name(), exc_info=True)
            self._show_error("Got Exception in function name :: " +
                           self._get_function_name() + ", try again")
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
            self.logger.error(e)
            self.logger.error('Exceptions raised in %s ',self._get_function_name(),exc_info=True)
            self._show_error("Got Exception in function name :: " + self._get_function_name() + ", try again")
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
                #self.logger.info("API: " + url + ",data: " + json.dumps(payload,sort_keys=True))
                print("URL: " + url + " data: " + payload)
                #response = mysession.post(url, data=json.dumps(payload, sort_keys= True))
                response = mysession.post(url,data=payload)
                self.logger.info("LOGIN RESPONSE: " + response.text)
                json_resp = json.loads(response.text)
                if json_resp['status']:
                    self._session_token = response.headers['Set-Cookie']
                    print("connection established with session token: [%s]" % self._session_token)
                    return True
                else:
                    raise requests.ConnectionError(
                        "Failed to connect. Server returned status=False")

            except requests.exceptions.Timeout:
                # TODO: user should have a way to figure out if required services are running or not? maybe some simple URL
                self._show_error("Timeout: Please check that the device is up and running and the IPC service is available")
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
            self.logger.error(e)
            self.logger.error('Exceptions raised in %s ',
                              self._get_function_name(), exc_info=True)
            self._show_error("Got Exception in function name :: " +
                             self._get_function_name() + ", try again")
            raise
