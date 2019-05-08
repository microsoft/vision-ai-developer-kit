# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

import argparse
import sys
import time
import subprocess
import utility
import os
import iot
import logging
import json

logging.basicConfig(level=logging.DEBUG)

from camera import CameraClient
restartCamera = False
mypushmodel = False
def main(protocol=None):

    logging.debug("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--pushmodel',help ='sets whether to push the model and required files to device or not', default=False)
    parser.add_argument('--ip', help='ip address of the camera', default=utility.getWlanIp())
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    if args.pushmodel is not None:
        mypushmodel = args.pushmodel
        logging.debug("setting value from argu -p pushmodel to :: %s" % mypushmodel)

    ip_addr = args.ip
    username = args.username
    password = args.password
    #getting Iot hub sdk ready with hub manager
    hub_manager = iot.HubManager()
    logging.debug("value of restartCamera is :: " + str(iot.restartCamera))

    #Connecting to camer using ipcWebServer SDK and turing camera on and then starting inferencing 
    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        #transferring model files to camera for inferencing 
        utility.transferdlc(mypushmodel)
        #this call we set the camera to dispaly over HDMI 
        logging.debug(camera_client.configure_preview(resolution="1080P",encode="AVC/H.264",bitrate="1.5Mbps",display_out=1))
        # this call turns on the camera and start transmetting over RTSP and HDMI  
        camera_client.set_preview_state("on")    
        #rtsp stream address 
        rtsp_stream_addr = str(camera_client.preview_url)
        logging.debug("rtsp stream is :: " + rtsp_stream_addr)
        #uploading rtsp stream address to iot hub as twin property so that user one can know what there rtsp address is and then use it on vlc media player 
        hub_manager.iothub_client_sample_run(rtsp_stream_addr)
        #Vam(Video analytics engine ) this will take the model and run on thee device 
        camera_client.set_analytics_state("on")
        logging.debug(camera_client.vam_url)
        # this will set the frames to be overlayed with information recieved from inference results ffrom your model
        camera_client.configure_overlay("inference")
        #Turning overlay to Truse to see inferencing frame overlayed with inference results
        camera_client.set_overlay_state("on")
        # heer we will use gstreamer to get the inference results from camera into thsi module and then send them up to cloud or another module
        try:
            while(True):
                with camera_client.get_inferences() as results:
                    print_inferences(results,camera_client,hub_manager)
                    print("Restarting get inference and print again!!!")
        except KeyboardInterrupt:
            logging.debug("Stopping")

        # turning everything off and logging out ...
        camera_client.set_overlay_state("off")
        camera_client.set_analytics_state("off")
        camera_client.set_preview_state("off")

def print_inferences(results=None, camera_client=None,hub_manager=None):
    logging.debug("")
    startTime = time.time()
    for result in results:
        if iot.restartCamera :
            logging.info(iot.restartCamera)
            restartInference(camera_client,hub_manager)
            return
            #restartCam(camera_client,hub_manager)
        if result is not None and result.objects is not None and len(result.objects):
            timestamp = result.timestamp
            if timestamp:
                logging.info("timestamp={}".format(timestamp))
            else:
                logging.info("timestamp= " + "None")
            for object in result.objects:
                if iot.restartCamera :
                    logging.info(iot.restartCamera)
                    restartInference(camera_client,hub_manager)
                    return
                    #restartCam(camera_client,hub_manager)
                id = object.id
                label = object.label
                confidence = object.confidence
                x = object.position.x
                y = object.position.y
                w = object.position.width
                h = object.position.height                
                logging.info("id={}".format(id))
                logging.info("label={}".format(label))
                logging.info("confidence={}".format(confidence))
                location = "Position(x,y,w,h)=" + str(x) + "," + str(y) + "," + str(w) + "," + str(h)
                logging.info(location)
                result = {"label":label,
                            "confidence":confidence}
                            #"location" : location}
                dataToCloud= json.dumps(result)
                #Checking if time to send message to make sure we are not sending more messages then set in twin 
                if(time.time() - startTime > iot.FreqToSendMsg):
                    #Checking if Object Of Interest returned from tarined mdoel is found to send alert to cloud

                    if(iot.ObjectOfInterest=="ALL" or iot.ObjectOfInterest.lower() in label.lower()):
                        logging.info("I see " + str(label) + " with confidence :: " + str(confidence))
                        hub_manager.SendMsgToCloud(dataToCloud)
                        startTime = time.time()
                    else:
                        logging.debug("Not sending to cloud as notification is set for only label::" + iot.ObjectOfInterest)
                else:
                    logging.debug("skipping sending msg to cloud until :: " + str(iot.FreqToSendMsg - ((time.time() - startTime))))
                logging.debug("")
        else:
            logging.debug("No results")
            if iot.restartCamera :
                logging.info(iot.restartCamera)
                restartInference(camera_client,hub_manager)
                return

def restartInference(camera_client = None,hub_manager = None) :
    iot.restartCamera = False
    try:
        logging.debug("Restarting VAM to apply new model config")
        camera_client.set_overlay_state("off")
        camera_client.set_analytics_state("off")
        time.sleep(1)
        camera_client.set_analytics_state("on")
        camera_client.set_overlay_state("on")
    except:
        logging.debug("we have got issue during vam ON off after camer switch ")
        restartCam(camera_client,hub_manager)
        #TO DO 
        # Try recovery here 
    
def restartCam(camera_client = None,hub_manager = None):
    try:
        iot.restartCamera = False

        # turning everything off and logging out ...
        camera_client.logout()
        if camera_client is not None:
            camera_client = None
        utility.CallSystemCmd("systemctl restart qmmf-webserver")
        time.sleep(1)
        utility.CallSystemCmd("systemctl restart ipc-webserver")
        time.sleep(1)
        ip_addr = utility.getWlanIp()
        with CameraClient.connect(ip_address=ip_addr, username='admin', password='admin') as camera_client:
            #this call we set the camera to dispaly over HDMI 
            #logging.debug(camera_client.configure_preview(resolution="1080P",display_out=1))
            # this call turns on the camera and start transmetting over RTSP and HDMI a stream from camera 
            camera_client.set_preview_state("on")
            #Vam(Video analytics engine ) this will take the model and run on thee device 
            camera_client.set_analytics_state("on")
            logging.debug(camera_client.vam_url)
            # this will set the frames to be overlayed with information recieved from inference results ffrom your model
            camera_client.configure_overlay("inference")
            #Turning overlay to Truse to see inferencing frame overlayed with inference results
            camera_client.set_overlay_state("on")
    except:
        logging.debug("we have got issue during Logout and Login restarting camera now...")
        utility.CallSystemCmd("systemctl restart")

    
if __name__ == '__main__':
    main()