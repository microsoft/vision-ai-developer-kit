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
from . error_utils import CameraClientError, log_unknown_exception
from . properties import Properties
from . model_utility import ModelUtility
from . inference import Inference
from iotccsdk import CameraClient
from iothub_client import IoTHubModuleClient, IoTHubTransportProvider, IoTHubError
from iothub_client import IoTHubMessage, DeviceMethodReturnValue
import time


TURN_CAMERA_ON_METHOD_NAME = "StartCamera"
TURN_CAMERA_OFF_METHOD_NAME = "StopCamera"

TO_UPSTREAM_MESSAGE_QUEUE_NAME = "ToUpstream"
MODULE_TWIN_UPDATE_CONTEXT = 0


# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
PROTOCOL = IoTHubTransportProvider.MQTT

ipc_provider = None
camera_client = None
hub_manager = None
properties = None
model_util = None


# Callback received when the message that we're forwarding is processed.
def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print("Confirmation[%d] received for message with result = %s" % (
        user_context, result))
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print("    Properties: %s" % key_value_pair)
    SEND_CALLBACKS += 1
    print("    Total calls confirmed: %d" % SEND_CALLBACKS)


def turn_camera_on_callback(payload, user_context):
    retval = DeviceMethodReturnValue()
    # TODO: actually turn_camera_on()
    return retval


def turn_camera_off_callback(payload, user_context):
    camera_client.set_overlay_state("off")
    camera_client.set_analytics_state("off")
    camera_client.set_preview_state("off")
    return


# Function will be called each time a direct method call is received
def method_callback(method_name, payload, user_context):
    retval = {
        TURN_CAMERA_ON_METHOD_NAME:
            lambda payload, user_context: turn_camera_on_callback(
                payload, user_context),
        TURN_CAMERA_OFF_METHOD_NAME:
            lambda payload, user_context: turn_camera_off_callback(
                payload, user_context)
    }[method_name](payload, user_context)

    return retval


def module_twin_callback(update_state, payload, user_context):
    print("Twin callback")
    global properties
    properties.handle_twin_update(payload)
    update_model_and_config()


def create_camera(ip_address=None, username="admin", password="admin"):
    if ip_address is None:
        ip_address = model_util.getWlanIp()

    print("ip address = %s" % ip_address)
    if ipc_provider is None:
        print("create camera with no ipc_provider")
        return CameraClient.connect(ip_address=ip_address,
                                    username=username, password=password)
    print("create camera with ipc_provider %s" % ipc_provider)
    return CameraClient.connect(ipc_provider=ipc_provider, ip_address=ip_address,
                                username=username, password=password)


def print_inference(result=None, hub_manager=None, last_sent_time=time.time()):
    global properties
    if (time.time() - last_sent_time <= properties.model_properties.message_delay_sec
            or result is None
            or result.objects is None
            or len(result.objects) == 0):
        return last_sent_time

    for inf_obj in result.objects:
        print("found result object")
        inference = Inference(inf_obj)
        if (properties.model_properties.is_object_of_interest(inference.label)):
            json_message = inference.to_json()
            hub_manager.send_message_to_upstream(json_message)
            print(json_message)
            last_sent_time = time.time()
    return last_sent_time


def update_model_and_config():
    global properties
    model_props = properties.model_properties
    camera_props = properties.camera_properties
    if camera_client is None or hub_manager is None:
        print("Handle updates aborting")
        print("camera_client is %s" % camera_client)
        print("hub_manager is %s" % hub_manager)
        return
    try:
        is_model_changed = model_props.update_inference_model()
        camera_props.configure_camera_client(camera_client, is_model_changed)
        properties.report_properties_to_hub(hub_manager)
    except Exception as ex:
        log_unknown_exception(
            "Error raised while handling update callback", hub_manager)
        raise ex
        model_util.restart_camera(camera_client)


class HubManager(object):
    def __init__(
            self,
            protocol=IoTHubTransportProvider.MQTT):
        print("Create manager")
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)

    def subscribe_to_events(self):
        print("subscribing to method calls")
        self.client.set_module_method_callback(method_callback, 0)

        print("subscribing to module twin updates")
        self.client.set_module_twin_callback(
            module_twin_callback, MODULE_TWIN_UPDATE_CONTEXT)

    # sends a messager to the "ToUpstream" queue to be sent to hub
    def send_message_to_upstream(self, message):
        try:
            message = IoTHubMessage(message)
            self.client.send_event_async(
                TO_UPSTREAM_MESSAGE_QUEUE_NAME, message, send_confirmation_callback, 0)
            # logging.info("finished sending message...")
        except Exception:
            print("Exception in SendMsgToCloud")
            pass


def main(protocol):
    global ipc_provider
    global camera_client
    global hub_manager
    global properties
    global model_util

    print("create model_util")
    model_util = ModelUtility()

    print("create properties")
    properties = Properties()
    camera_props = properties.camera_properties

    hub_manager = HubManager(protocol)

    # push model
    model_util.transfer_dlc(False)

    print("\nPython %s\n" % sys.version)
    last_time = time.time()

    while True:
        with create_camera() as camera_client:
            try:
                ipc_provider = camera_client.ipc_provider
                camera_props.configure_camera_client(camera_client)
                properties.report_properties_to_hub(hub_manager)
                hub_manager.subscribe_to_events()
                while True:
                    try:
                        while camera_client.vam_running:
                            with camera_client.get_inferences() as results:
                                for result in results:
                                    last_time = print_inference(
                                        result, hub_manager, last_time)
                    except EOFError:
                        print("current vam state: %s" %
                              camera_client.vam_running)
                    except Exception:
                        log_unknown_exception(
                            "exception from get inferences", hub_manager)
                        continue
            except CameraClientError:
                print("Got camera error will try to continue")
                if camera_client is not None:
                    status = camera_client.logout()
                    print("logout with status: %s" % status)
                camera_client = None
                continue
            except IoTHubError as iothub_error:
                print("Unexpected error %s from IoTHub" % iothub_error)
                return
            except KeyboardInterrupt:
                print("IoTHubModuleClient sample stopped")
                return
            finally:
                print("try to clean up before the end")
                if camera_client is not None:
                    camera_client.set_overlay_state("off")
                    camera_client.set_analytics_state("off")
                    camera_client.set_preview_state("off")
                    status = camera_client.logout()
                    print("logout with status: %s" % status)


if __name__ == '__main__':
    main(PROTOCOL)
