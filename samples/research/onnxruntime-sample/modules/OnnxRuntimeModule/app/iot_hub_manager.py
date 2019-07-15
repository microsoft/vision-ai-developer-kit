# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
from camera import CameraClient
from iothub_client import IoTHubClient, IoTHubMessage, IoTHubModuleClient, IoTHubMessageDispositionResult,IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult, IoTHubError

TO_UPSTREAM_MESSAGE_QUEUE_NAME = "ToUpstream"

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

# global counters
send_callbacks = 0

class IotHubManager(object):
    TIMER_COUNT = 2

    def __init__(self, protocol, camera_client: CameraClient):
        print("Creating IoT Hub manager")
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        self.camera_client = camera_client

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)

    # sends a messager to the "ToUpstream" queue to be sent to hub
    def send_message_to_upstream(self, message):
        try:
            message = IoTHubMessage(message)
            self.client.send_event_async(
                TO_UPSTREAM_MESSAGE_QUEUE_NAME,
                message,
                self.__send_confirmation_callback,
                0)
            # logging.info("finished sending message...")
        except Exception as ex:
            print("Exception in send_message_to_upstream: %s" % ex)
            pass

    # Callback received when the message that we're forwarding is processed.
    def __send_confirmation_callback(self, message, result, user_context):
        global send_callbacks
        print("Confirmation[%d] received for message with result = %s" % (
            user_context, result))
        map_properties = message.properties()
        key_value_pair = map_properties.get_internals()
        print("\tProperties: %s" % key_value_pair)
        send_callbacks += 1
        print("\tTotal calls confirmed: %d" % send_callbacks)

    def send_reported_state_callback(self, status_code, user_context):
        print ( "" )
        print ( "Confirmation for reported state called with:" )
        print ( "    status_code: %d" % status_code )

    def send_property(self, prop):
        try:            
            if self.client.protocol == IoTHubTransportProvider.MQTT:
                self.client.send_reported_state(prop,
                                                len(prop), 
                                                self.send_reported_state_callback, 
                                                prop)                                                
        except Exception as ex:
            print("Exception in send_property: %s" % ex)

