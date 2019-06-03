# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.


import argparse
import sys
import time
import subprocess
import utility
import os
import logging
import json
from iot import HubManager,msg_per_minute,object_of_interest
from camera import CameraClient


logging.basicConfig(level=logging.INFO)
import threading


PUSH_MODEL = False

def init(protocol=None):
    global PUSH_MODEL
    logging.info("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()

  
    #parser.add_argument('-p','--pushmodel',help ='sets whether to push the model and required files to device or not',type=bool, default=False)
    parser.add_argument('--ip', help='ip address of the camera', default=utility.getWlanIp())
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    """ if args.pushmodel is not None:
        mypushmodel = args.pushmodel
        logging.info("setting value from args.pushmodel :: %s" % args.pushmodel)
        logging.info("setting value from argu -p pushmodel to :: %s" % mypushmodel) """

    ip_addr = args.ip
    username = args.username
    password = args.password
    try:
        #Connecting to camer using ipcWebServer SDK and turing camera on and then starting inferencing 
        with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
            
            #getting Iot hub sdk ready with hub manager
            hub_manager = HubManager(camera_client)
            #transferring model files to camera for inferencing 
            utility.transferdlc(PUSH_MODEL)
            #this call we set the camera to dispaly over HDMI 
            logging.info(camera_client.configure_preview(resolution="1080P",encode="AVC/H.264",bitrate="1.5Mbps",display_out=1))
            # this call turns on the camera and start transmetting over RTSP and HDMI  
            camera_client.set_preview_state("on") 
            # setting camera handler that we will use to sync camera and IoT Hub 
            #camera_handler = CameraIoTHandler(camera_client)
            #rtsp stream address 
            rtsp_stream_addr = str(camera_client.preview_url)
            logging.info("rtsp stream is :: " + rtsp_stream_addr)

            #uploading rtsp stream address to iot hub as twin property so that user one can know what there rtsp address is and then use it on vlc media player 
            hub_manager.iothub_client_sample_run(rtsp_stream_addr)

            #Vam(Video analytics engine ) this will take the model and run on thee device 
            if(not camera_client.vam_running):
                camera_client.set_analytics_state("on")
            logging.info(camera_client.vam_url)
            # this will set the frames to be overlayed with information recieved from inference results ffrom your model
            camera_client.configure_overlay("inference")
            #Turning overlay to True to see inferencing frame overlayed with inference results
            camera_client.set_overlay_state("on")
            # heer we will use gstreamer to get the inference results from camera into thsi module and then send them up to cloud or another module
            try:
                while(True):
                    with camera_client.get_inferences() as results:
                        print_inferences(results,camera_client,hub_manager)
                        print("Restarting get inference and print again!!!")
                    time.sleep(2)
            except KeyboardInterrupt:
                logging.debug("Stopping")

            # turning everything off and logging out ...

            camera_client.set_overlay_state("off")
            camera_client.set_analytics_state("off")
            camera_client.set_preview_state("off")
            #Vam(Video analytics machine) this will take the model and run on the device 

    except Exception as e:
            logging.info("Encountered an issue during camera intialization; restarting camera now.")
            logging.info("Clearing all models and using the container default model configuration.")
            utility.transferdlc(True)
            #send_system_cmd("systemctl reboot")
            logging.exception(e)
            raise

def print_inferences(results=None, camera_client=None,hub_manager=None):

    logging.debug("")
    startTime = time.time()
    for result in results:
        if result is not None and result.objects is not None and len(result.objects):
            timestamp = result.timestamp
            if timestamp:
                logging.debug("timestamp={}".format(timestamp))
            else:
                logging.debug("timestamp= " + "None")
            for object in result.objects:
                id = object.id
                label = object.label
                confidence = object.confidence
                x = object.position.x
                y = object.position.y
                w = object.position.width
                h = object.position.height                
                logging.debug("id={}".format(id))
                logging.debug("label={}".format(label))
                logging.debug("confidence={}".format(confidence))
                location = "Position(x,y,w,h)=" + str(x) + "," + str(y) + "," + str(w) + "," + str(h)
                logging.debug(location)
                result = {"label":label,
                            "confidence":confidence}
                dataToCloud= json.dumps(result)
                #Checking if time to send message to make sure we are not sending more messages then set in twin 
                if(time.time() - startTime > msg_per_minute):
                    #Checking if Object Of Interest returned from tarined mdoel is found to send alert to cloud
                    if(object_of_interest=="ALL" or object_of_interest.lower() in label.lower()):
                        logging.info("I see " + str(label) + " with confidence :: " + str(confidence))
                        hub_manager.SendMsgToCloud(dataToCloud)
                        startTime = time.time()
                    else:
                        logging.debug("Not sending to cloud as notification is set for only label::" + object_of_interest)
                else:
                    logging.debug("skipping sending msg to cloud until :: " + str(msg_per_minute - ((time.time() - startTime))))
                logging.debug("")
        else:
            logging.debug("No results")

if __name__ == '__main__':
    init()