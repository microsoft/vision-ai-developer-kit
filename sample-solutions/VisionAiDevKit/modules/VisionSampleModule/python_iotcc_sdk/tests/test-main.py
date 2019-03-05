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


from iotcc.sdk.camera import CameraClient

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

    #getting Iot hub sdk ready with hub manager
    hub_manager = iot.HubManager()

    #Connecting to camer using ipcWebServer SDK and turing camera on and then starting inferencing 
    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        #transferring model files to camera for inferencing 
        if mypushmodel.find("True") == -1 :
            print("Not transferring dlc  as per parameter passed")
        else :
            print("transferring model ,label and va config file as set in create option with -p %s passed" % mypushmodel)
            utility.transferdlc()
        
        #this call we set the camera to dispaly over HDMI 
        print(camera_client.configure_preview(display_out=1))
        # this call turns on the camera and start transmetting over RTSP and HDMI a stream from camera 
        camera_client.toggle_preview(True)
        time.sleep(1)
        #rtsp stream address 
        rtsp_stream_addr = "rtsp://" + ip_addr + ":8900/live"
        #uploading rtsp stream address to iot hub as twin property so that user one can know what there rtsp address is and then use it on vlc media player 
        hub_manager.iothub_client_sample_run(rtsp_stream_addr)

        #Vam(Video analytics engine ) this will take the model and run on thee device 
        camera_client.toggle_vam(True)
        
        # this will set the frames to be overlayed with information recieved from inference results ffrom your model
        camera_client.configure_overlay("inference")

        #Turning overlay to Truse to see inferencing frame overlayed with inference results
        camera_client.toggle_overlay(True)

        # heer we will use gstreamer to get the inference results from camera into thsi module and then send them up to cloud or another module
        try:
            with camera_client.get_inferences() as results:
                print_inferences(hub_manager,results)
        except KeyboardInterrupt:
            print("Stopping")
        try:
            while(True):
                time.sleep(2)
        except KeyboardInterrupt:
            print("Stopping")

        # turning everything off and logging out ...
        camera_client.toggle_overlay(False)

        camera_client.toggle_vam(False)

        camera_client.toggle_preview(False)




def print_inferences(hub_manager,results=None):
    print("")
   
    for result in results:
        if result is not None and result.objects is not None and len(result.objects):
            timestamp = result.timestamp
            #if timestamp:
                #print("timestamp={}".format(timestamp))
            #else:
                #print("timestamp= " + "None")
            for object in result.objects:
                id = object.id
                label = object.label
                confidence = object.confidence
                x = object.position.x
                y = object.position.y
                w = object.position.width
                h = object.position.height
                print("id={}".format(id))
                print("label={}".format(label))
                print("confidence={}".format(confidence))
                print("Position(x,y,w,h)=({},{},{},{})".format(x, y, w, h))
                print("")
                #Sending inference results back to cloud ....

                hub_manager.SendMsgToCloud("I see " + str(label) + " with confidence :: " + str(confidence))
                time.sleep(1)
        else:
            print("No results")

if __name__ == '__main__':
    main()
