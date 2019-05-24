# ==============================================================================
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.
# ==============================================================================

#pylint: disable=E0611

import time
import os
import subprocess as sp
import sys
import shutil
import socket

#from main import my_camera_client
import logging
logging.basicConfig(level=logging.INFO)
from utility import get_file_zip
import iothub_client
from iothub_client import IoTHubClient, IoTHubMessage, IoTHubModuleClient, IoTHubMessageDispositionResult,IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult, IoTHubError

import json 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0

inference_files_zip_url =""
model_url = ""
label_url = ""
config_url = ""
restartCamera = False
msg_per_minute = 5
wait_for_minutes = 12
object_of_interest = "ALL"
start_time = 0




def send_reported_state_callback(status_code, user_context):
    print ( "" )
    print ( "Confirmation for reported state called with:" )
    print ( "    status_code: %d" % status_code )

# Callback received when the message that we're forwarding is processed.
def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    logging.info ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    logging.info ( "    Properties: %s" % key_value_pair )
    SEND_CALLBACKS += 1
    logging.info ( "    Total calls confirmed: %d" % SEND_CALLBACKS )


# receive_message_callback is invoked when an incoming message arrives on the specified 
# input queue (in the case of this sample, "input1").  Because this is a filter module, 
# we will forward this message onto the "output1" queue.
def receive_message_callback(message, hubManager):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    hubManager.forward_event_to_output("output1", message, 0)
    return IoTHubMessageDispositionResult.ACCEPTED

class HubManager(object):

    TIMER_COUNT = 2
    
    TWIN_CONTEXT = 0 
    SEND_REPORTED_STATE_CONTEXT = 0

    def __init__(
            self,
            camera_handle,protocol=IoTHubTransportProvider.MQTT):
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        self.iot_camera_handle = camera_handle
        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)
        
        # sets the callback when a message arrives on "input1" queue.  Messages sent to 
        # other inputs or to the default will be silently discarded.
        self.client.set_message_callback("input1", receive_message_callback, self)
        self.client.set_module_twin_callback(self.module_twin_callback, self)
       

    # Forwards the message received onto the next stage in the process.
    def forward_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(
            outputQueueName, event, send_confirmation_callback, send_context)
    
    def iothub_client_sample_run(self,message):
        try:
            
            if self.client.protocol == IoTHubTransportProvider.MQTT:
                print ( "Sending data as reported property..." )
                reported_state = "{\"rtsp_addr\":\"" + message + "\"}"
                self.client.send_reported_state(reported_state, len(reported_state), send_reported_state_callback, self.SEND_REPORTED_STATE_CONTEXT)
                status_counter = 0
                while status_counter <= self.TIMER_COUNT:
                    status = self.client.get_send_status()
                    time.sleep(2)
                    status_counter += 1 
             
        except IoTHubError as iothub_error:
            print ( "Unexpected error %s from IoTHub" % iothub_error )
            return
        except KeyboardInterrupt:
            print ( "IoTHubClient sample stopped" )

    def SendMsgToCloud(self, msg):
        try :
            #logging.info("sending message...")
            message=IoTHubMessage(msg)
            self.client.send_event_async(
                "output1", message, send_confirmation_callback, 0)
            logging.info("finished sending message...")
        except Exception :
            print ("Exception in SendMsgToCloud")
            pass
    def module_twin_callback(self,update_state, payload, user_context):
        global inference_files_zip_url
        global model_url
        global label_url
        global config_url
        global msg_per_minute
        global wait_for_minutes
        global object_of_interest 
        print ( "" )
        print ( "Twin callback called with:" )
        print ( "    updateStatus: %s" % update_state )
        print ( "    payload: %s" % payload )
        data = json.loads(payload)
        setRestartCamera = False

        if "desired" in data and "inference_files_zip_url" in data["desired"]:
            dst_folder="twin_provided_model"
            inference_files_zip_url = data["desired"]["inference_files_zip_url"]
            if inference_files_zip_url:
                print("Setting value to %s from ::  data[\"desired\"][\"all_inference_files_zip\"]" % inference_files_zip_url)
                setRestartCamera = get_file_zip(inference_files_zip_url,dst_folder)
            else:
                print(inference_files_zip_url)
        if "inference_files_zip_url" in data:
            dst_folder="twin_provided_model"
            inference_files_zip_url = data["inference_files_zip_url"]
            if inference_files_zip_url:
                print("Setting value to %s from ::  data[\"all_inference_files_zip\"]" % inference_files_zip_url)
                setRestartCamera = get_file_zip(inference_files_zip_url,dst_folder)
            else:
                print(inference_files_zip_url)

        if "desired" in data and "msg_per_minute" in data["desired"]:
            
            msg_per_minute = data["desired"]["msg_per_minute"]
            msg_per_minute = 60/int(msg_per_minute)
            print("Setting value to %s from ::  data[\"msg_per_minute\"]" % msg_per_minute)

        if "msg_per_minute" in data:
            msg_per_minute = data["msg_per_minute"]
            wait_for_minutes = int(60/int(msg_per_minute))

            print("Setting value to %s from ::  data[\"msg_per_minute\"]" % msg_per_minute)

        if "desired" in data and "object_of_interest" in data["desired"]:
            object_of_interest = data["desired"]["object_of_interest"]
            print("Setting value to %s from ::  data[\"object_of_interest\"]" % object_of_interest)

        if "object_of_interest" in data:
            msg_per_minute = data["object_of_interest"]
            print("Setting value to %s from ::  data[\"object_of_interest\"]" % object_of_interest)
                
        if setRestartCamera:
            #
            try:
                logger.info("Restarting VAM to apply new model config")
                self.restartInference(self.iot_camera_handle)
                
            except Exception as e:
                logger.info("Got an issue during vam ON off after twin update")
                logger.exception(e)
                raise
    def restartInference(self,camera_client) :
        try:

            logger.debug("Restarting VAM to apply new model config")
            camera_client.set_overlay_state("off")
            if(camera_client.vam_running):
                camera_client.set_analytics_state("off")
            #time.sleep(1)
            camera_client.set_analytics_state("on")
            camera_client.set_overlay_state("on")
            #self.print_and_send_results()

        except Exception as e:
            logger.debug("System got an exception during vam ON off after twin model update!!! ")
            logger.exception(e)
            #self.restart_cam(camera_client)
            raise
    
 



        