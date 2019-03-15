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
from camera import CameraClient

def main(protocol=None):
    print("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', help='ip address of the camera', default=utility.getWlanIp())
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    ip_addr = args.ip
    username = args.username
    password = args.password
    ip_addr = '127.0.0.1'
    hub_manager = iot.HubManager()

    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        #transferring model files to device
        isTransfer = str(os.getenv("TRANSFER_DLC_MODEL", "True"))
        if isTransfer == "True":
            utility.transferdlc()
            print('Transfer dlc model files to device: YES.')
        else:
            print('Transfer dlc model files to device: NO.')

        print(camera_client.configure_preview(display_out=1))

        camera_client.toggle_preview(True)
        time.sleep(15)
        rtsp_ip = utility.getWlanIp()
        rtsp_stream_addr = "rtsp://" + rtsp_ip + ":8900/live"
        hub_manager.iothub_client_sample_run(rtsp_stream_addr)

        camera_client.toggle_vam(True)

        camera_client.configure_overlay("inference")

        camera_client.toggle_overlay(True)
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

        camera_client.toggle_overlay(False)

        camera_client.toggle_vam(False)

        camera_client.toggle_preview(False)

def get_model_config():
    # TODO: get the AML model and return an AiModelConfig
    return None



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
                hub_manager.SendMsgToCloud("I see " + str(label) + " with confidence :: " + str(confidence))
                time.sleep(1)
        else:
            print("No results")

if __name__ == '__main__':
    main()
