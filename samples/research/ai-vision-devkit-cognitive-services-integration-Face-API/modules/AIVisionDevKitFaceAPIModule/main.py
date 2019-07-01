# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import sys
if __package__ == '' or __package__ is None:  # noqa
    import os
    parent_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(1, parent_dir)
    pkg_name = os.path.split(os.path.dirname(os.path.abspath(__file__)))[-1]
    __import__(pkg_name)
    __package__ = str(pkg_name)
    del os
from . constants import SETTING_OFF
from . error_utils import CameraClientError, log_unknown_exception
from . properties import Properties
from . model_utility import ModelUtility
from . inference import Inference
from . iot_hub_manager import IotHubManager
from iotccsdk import CameraClient
from iothub_client import IoTHubTransportProvider, IoTHubError
import time
import subprocess
import os
import threading
from pathlib import Path
from . azure_face_api import azure_face_api_detect

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
IOT_HUB_PROTOCOL = IoTHubTransportProvider.MQTT

ipc_provider = None
camera_client = None
iot_hub_manager = None
properties = None
model_util = None


def create_camera(ip_address=None, username="admin", password="admin"):
    if ip_address is None:
        ip_address = model_util.getWlanIp()

    print("ip address = %s" % ip_address)
    if ipc_provider is None:
        print("Create camera with no ipc_provider")
        return CameraClient.connect(
            ip_address=ip_address,
            username=username,
            password=password)

    print("Create camera with ipc_provider %s" % ipc_provider)
    return CameraClient.connect(
        ipc_provider=ipc_provider,
        ip_address=ip_address,
        username=username,
        password=password)


def print_inference(result=None, hub_manager=None, last_sent_time=time.time()):
    global properties
    if (time.time() - last_sent_time <= properties.model_properties.message_delay_sec
            or result is None
            or result.objects is None
            or len(result.objects) == 0):
        return last_sent_time

    for inf_obj in result.objects:
        print("Found result object")
        inference = Inference(inf_obj)
        if (properties.model_properties.is_object_of_interest(inference.label)):
            json_message = inference.to_json()
            iot_hub_manager.send_message_to_upstream(json_message)
            print(json_message)
            last_sent_time = time.time()
    return last_sent_time


def is_person(result=None, last_sent_time=time.time()):
    global properties
    if (time.time() - last_sent_time <= properties.model_properties.message_delay_sec
            or result is None
            or result.objects is None
            or len(result.objects) == 0):
        return False

    for inf_obj in result.objects:
        print("Found result object")
        inference = Inference(inf_obj)
        if (inference.label == 'person' or inference.label == 'person.'):
            return True
    return False


def main(protocol):
    global ipc_provider
    global camera_client
    global iot_hub_manager
    global properties
    global model_util

    print("Create model_util")
    model_util = ModelUtility()

    print("Create properties")
    properties = Properties()
    camera_props = properties.camera_properties

    # push model
    model_util.transfer_dlc(False)

    print("\nPython %s\n" % sys.version)
    last_time = time.time()

    while True:
        with create_camera() as camera_client:
            try:
                ipc_provider = camera_client.ipc_provider
                camera_props.configure_camera_client(camera_client)
                iot_hub_manager = IotHubManager(
                    protocol, camera_client, properties)
                iot_hub_manager.subscribe_to_events()
                if camera_client.vam_running:
                    camera_client.captureimage()

                while True:
                    try:
                        while camera_client.vam_running:
                            with camera_client.get_inferences() as results:
                                for result in results:
                                    if is_person(result, last_time):
                                        face_api_thread = threading.Thread(
                                            target=azure_face_api_detect,
                                            args=(camera_client, iot_hub_manager))
                                        face_api_thread.start()
                                    last_time = print_inference(
                                        result, iot_hub_manager, last_time)
                    except EOFError:
                        print("EOFError. Current VAM running state is %s." %
                              camera_client.vam_running)
                    except Exception:
                        log_unknown_exception(
                            "Exception from get inferences", iot_hub_manager)
                        continue
            except CameraClientError as cce:
                print("Received camera error, but will try to continue: %s" % cce)
                if camera_client is not None:
                    status = camera_client.logout()
                    print("Logout with status: %s" % status)
                camera_client = None
                continue
            except IoTHubError as iothub_error:
                print("Unexpected error %s from IoTHub" % iothub_error)
                return
            except KeyboardInterrupt:
                print("IoTHubModuleClient sample stopped")
                return
            finally:
                print("Try to clean up before the end")
                if camera_client is not None:
                    camera_client.set_overlay_state(SETTING_OFF)
                    camera_client.set_analytics_state(SETTING_OFF)
                    camera_client.set_preview_state(SETTING_OFF)
                    status = camera_client.logout()
                    print("Logout with status: %s" % status)


if __name__ == '__main__':
    main(IOT_HUB_PROTOCOL)
