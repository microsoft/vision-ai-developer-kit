# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

import argparse
import sys
import time
import subprocess
import os

from camera import CameraClient

import utility
import traceback



def main(protocol=None):
    print("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--pushmodel',help ='sets whether to push the model and required files to device or not', default=True)
    parser.add_argument('--ip', help='ip address of the camera', default=utility.getWlanIp())
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    if args.pushmodel is not None:
        mypushmodel = args.pushmodel
        print("setting value from argu -p pushmodel to :: %s" % mypushmodel)
    ip_addr = args.ip
    username = args.username
    password = args.password

    #Please change this address to camer ip address can be found by using adb shell -> ifconfig
    ip_addr = '192.168.0.103'
    #hub_manager = iot.HubManager()
    #utility.transferdlc()
    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
      
        #this call we set the camera to dispaly over HDMI 
        print(camera_client.configure_preview(resolution="1080P",display_out=1))
        # this call turns on the camera and start transmetting over RTSP and HDMI a stream from camera 
        camera_client.set_preview_state("on")
       
        #rtsp stream address 
        
        rtsp_stream_addr = str(camera_client.preview_url)
        print("rtsp stream is :: " + rtsp_stream_addr)

        if not camera_client.captureimage():
            print("captureimage failed")
        #Vam(Video analytics engine ) this will take the model and run on thee device 
        camera_client.set_analytics_state("on")
        print(camera_client.vam_url)
        
        # this will set the frames to be overlayed with information recieved from inference results ffrom your model
        camera_client.configure_overlay("inference")

        #Turning overlay to Truse to see inferencing frame overlayed with inference results
        camera_client.set_overlay_state("on")

        # heer we will use gstreamer to get the inference results from camera into thsi module and then send them up to cloud or another module
        try:
            with camera_client.get_inferences() as results:
                print_inferences(results, camera_client)
        except:
            print("Stopping")


def print_inferences(results=None, camera_client=None):
    print("")
    for result in results:
        if result is not None and result.objects is not None and len(result.objects):
            timestamp = result.timestamp
            if timestamp:
                print("timestamp={}".format(timestamp))
            else:
                print("timestamp= " + "None")
            for object in result.objects:
                id = object.id
                print("id={}".format(id))
                label = object.label
                print("label={}".format(label))
                confidence = object.confidence
                print("confidence={}".format(confidence))
                #if int(confidence) >= 90:
                    #if not camera_client.captureimage():
                        #print("captureimage failed for {}".format(label))
                x = object.position.x
                y = object.position.y
                w = object.position.width
                h = object.position.height
                print("Position(x,y,w,h)=({},{},{},{})".format(x, y, w, h))
                print("")
        else:
            print("No results")

if __name__ == '__main__':
    main()
