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
from camera import CameraClient
from camera_iot_handler import CameraIoTHandler
from camera_iot_handler import msg_per_minute,object_of_interest,send_system_cmd

logging.basicConfig(level=logging.INFO)
import threading


mypushmodel = False

def init(protocol=None):

    logging.info("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--pushmodel',help ='sets whether to push the model and required files to device or not', default=False)
    parser.add_argument('--ip', help='ip address of the camera', default=utility.getWlanIp())
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    if args.pushmodel is not None:
        mypushmodel = args.pushmodel
        logging.info("setting value from argu -p pushmodel to :: %s" % mypushmodel)

    ip_addr = args.ip
    username = args.username
    password = args.password
    try:
        #Connecting to camer using ipcWebServer SDK and turing camera on and then starting inferencing 
        with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
            #this call we set the camera to dispaly over HDMI 
            logging.info(camera_client.configure_preview(resolution="1080P",encode="AVC/H.264",bitrate="1.5Mbps",display_out=1))
            # this call turns on the camera and start transmetting over RTSP and HDMI  
            camera_client.set_preview_state("on") 
            # setting camera handler that we will use to sync camera and IoT Hub 
            camera_handler = CameraIoTHandler(camera_client)
            #transferring model files to camera for inferencing 
            utility.transferdlc(mypushmodel)
            #Vam(Video analytics engine ) this will take the model and run on thee device 
            if(not camera_client.vam_running):
                camera_client.set_analytics_state("on")
            #logging.info(camera_client.vam_url)
            # this will set the frames to be overlayed with information recieved from inference results ffrom your model
            camera_client.configure_overlay("inference")

            #Turning overlay to True to see inferencing frame overlayed with inference results
            camera_client.set_overlay_state("on")
            
            #uploading rtsp stream address to iot hub as twin property so that user one can know what there rtsp address is and then use it on vlc media player 
            camera_handler.send_rtsp_info()
            # heer we will use gstreamer to get the inference results from camera into thsi module and then send them up to cloud or another module
            try:
                while(True):
                    camera_handler.print_and_send_results()
                    time.sleep(4)
            except KeyboardInterrupt:
                logging.info("Stopping")

            # turning everything off and logging out ...
            camera_client.set_overlay_state("off")
            camera_client.set_analytics_state("off")
            camera_client.set_preview_state("off")
    except Exception as e:
            logging.debug("we have got issue during Logout and Login restarting camera now...")
            utility.transferdlc(True)
            send_system_cmd("systemctl reboot")
            logging.exception(e)
            raise

if __name__ == '__main__':
    init()