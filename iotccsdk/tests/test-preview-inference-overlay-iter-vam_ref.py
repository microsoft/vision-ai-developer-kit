# Copyright (c) 2019, The Linux Foundation. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#    * Neither the name of The Linux Foundation nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import sys
import socket
import time
import threading
import subprocess

from iotccsdk.camera import CameraClient

def getWlanIp():
    #if(os.name == "nt") :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        if IP.split('.')[0] == '172':
            print("Ip address detected is :: " + IP )
            IP = '127.0.0.1'
            print("Ip address changed to :: " + IP + "to avoid docker interface")
        print("Ip address detected is :: " + IP )

    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def main(protocol=None):
    #global camera_client
    print("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', help='ip address of the camera', default='127.0.0.1')
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    parser.add_argument('--iteration', help='Number of iterations', type=int, default=1)
    parser.add_argument('--runtime', help='runtime for each iteration', type=int, default=60)
    args = parser.parse_args()
    ip_addr = args.ip
    username = args.username
    password = args.password
    iter = args.iteration
    runtime = args.runtime

    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        print(camera_client.configure_preview(resolution="1080P", display_out=1))

        camera_client.set_preview_state("on")

        print(camera_client.preview_url)

        for x in range(0, iter):
            print("-------------------- Iteration {} - Start ---------------------".format(x+1))

            camera_client.set_analytics_state("on")
            print(camera_client.vam_url)
            print(" ANALYTICS STATE IS ON--")

            camera_client.configure_overlay("inference")
            print(" Overlay is configured--")

            camera_client.set_overlay_state("on")
            print(" OVERLAY STATE IS ON--")

            try:
                with camera_client.get_inferences() as results:
                    t = threading.Thread(target=print_inferences, args=(results,))
                    print(" BEFORE THREAD--")
                    t.start()
                    print(" AFTER START THREAD--sleep {}", format(runtime))
                    time.sleep(runtime)
            except:
                print("Stopping")

            print(" STOPPING OVERLAY--")
            camera_client.set_overlay_state("off")
            print(" STOPPING ANALYTICS--")
            camera_client.set_analytics_state("off")
            subprocess.run(["cp", "vam_model_folder/va-snpe-engine-library_config.json", "vam_model_folder/va-snpe-engine-library_config_temp.json"])
            subprocess.run(["cp", "vam_model_folder/va-snpe-engine-library_config_1.json", "vam_model_folder/va-snpe-engine-library_config.json"])
            subprocess.run(["cp", "vam_model_folder/va-snpe-engine-library_config_temp.json", "vam_model_folder/va-snpe-engine-library_config_1.json"])
            print(" OVERLAY AND ANALYTICS STATE IS OFF--")
            t.join()
            print("-------------------- Iteration {} - End --------------------".format(x+1))

        camera_client.set_preview_state("off")


def print_inferences(results=None):
    print("Starting prints")
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
                x = object.position.x
                y = object.position.y
                w = object.position.width
                h = object.position.height
                print("Position(x,y,w,h)=({},{},{},{})".format(x, y, w, h))
                print("")
        else:
            print("No results")
    print("Stoping prints")

if __name__ == '__main__':
    main()
