# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import threading
import cv2
import time
import datetime
import sys
import socket
import shutil
import json
import iothub_client
from camera import CameraClient
from iot_hub_manager import IotHubManager
from iothub_client import IoTHubTransportProvider, IoTHubError
from getmodel import TinyYOLOv2Class, YOLOV3Class, FasterRCNNClass

# Define model map
model_map = {
    'tinyyolov2': TinyYOLOv2Class,
    'yolov3': YOLOV3Class,
    'fasterrcnn': FasterRCNNClass
}

default_model = 'tinyyolov2'
model_name = default_model
model_class = None

# Handle SIGTERM signal when docker stops the current VisionSampleModule container
import signal
is_running = True
is_busy = False

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
IOT_HUB_PROTOCOL = IoTHubTransportProvider.MQTT

# Default to disable sending D2C messages to IoT Hub to prevent consuming network bandwidth 
# and reduce the frequency of cv2.VideoCapture() fail to capture frame from RTSP stream.
enable_iot = False
iot_hub_manager = None

# Define constants
new_frame = []

def detect_image():
    global new_frame
    global is_running
    global is_busy
    global model_class

    while (is_running):
        if (len(new_frame) == 0):
            #print('New frame not ready!')
            time.sleep(0.1)
            continue

        #print('Start detect image: {}' .format(datetime.datetime.utcnow()))        
        model_class.detect_image(new_frame)
        #print('End detect image: {}' .format(datetime.datetime.utcnow()))

        new_frame = []
        is_busy = False

def capture_frames(preview_url):
    global new_frame
    global model_class
    global is_busy

    # Get model_class 
    if model_name in model_map:
        model_class = model_map[model_name](iot_hub_manager)
    else:
        model_class = model_map[default_model](iot_hub_manager)

    # Start a thread to detect a captured frame    
    threading.Thread(target=detect_image, daemon=True, args=()).start()

    # Read rtsp stream and detect each frame

    # Note: Current OpenCV VideoCapture() has memory leak for reading RTST Steam:
    #       If your application is actual a little bit slower than your configured fps you got a memory leak.
    #       https://github.com/opencv/opencv/issues/5715
    
    while (is_running):
        new_frame = []
        has_frame = False

        cap = cv2.VideoCapture(preview_url)
        time.sleep(1)

        # Capture frame-by-frame
        while (is_running and cap.isOpened() == True):
            try:
                if is_busy:  # detect_image() thread hand't finished to detect the latest frame
                    has_frame = cap.grab()  # don't retrieve frame if the previous frame processing hadn't finished
                else:
                    has_frame, frame = cap.read()
                    if (has_frame)                                     :
                        new_frame = frame
                        is_busy = True

                # If WiFi connection speed is slow, cv2.VideoCapture(preview_url) will fail to capture frame frequently
                if not has_frame: 
                    new_frame = []
                    print("!!! No frame!  Restart cv2.VideoCapture()!")
                    print("!!! TimeStamp: {}" .format(datetime.datetime.utcnow()))
                    cap.release()
                    break

            except Exception as ex:
                print("Exception in detect_camera: %s" % ex)
                cap.release()
                break

    cap.release()

def getWlanIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        if IP.split('.')[0] == '172':
            print("Ip address detected is :: " + IP )
            IP = '172.17.0.1'
            print("Ip address changed to :: " + IP + "to avoid docker interface")
        print("Ip address detected is :: " + IP )
        
    except:
        IP = '172.17.0.1'
    finally:
        s.close()
    return IP

def main(protocol=None):
    global iot_hub_manager
    
    ip_addr = getWlanIp()
    username = 'admin'
    password = 'admin'

    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        try:                

            print('supported resolutions: ' + str(camera_client.resolutions))
            print('supported encodetype: ' + str(camera_client.encodetype))
            print('supported bitrates: ' + str(camera_client.bitrates))
            print('supported framerates: ' + str(camera_client.framerates))

            camera_client.configure_preview(resolution="1080P", encode='AVC/H.264', framerate=24, display_out=1)
            camera_client.set_preview_state("on")

            # Write rtsp_addr to twin
            preview_url = camera_client.preview_url
            iot_hub_manager = IotHubManager(protocol, camera_client)
            print ( "Sending rtsp_addr property..." )
            prop = {"rtsp_addr": preview_url}
            prop = json.dumps(prop)            
            iot_hub_manager.send_property(prop)

            if not enable_iot:  # won't send D2C messages to IoT Hub
                iot_hub_manager = None

            # Start to detect object
            preview_url = "rtsp://localhost:8900/live"  # comment it if running by pure docker run
            capture_frames(preview_url)

        except IoTHubError as iothub_error:
            print("Unexpected error %s from IoTHub" % iothub_error)
            return
        
        except Exception as ex:
            print("Exception in main(): {}" .format(ex))
            return

        finally:
            print("Stop preview before exit.")
            if camera_client is not None:
                camera_client.set_preview_state("off")
                status = camera_client.logout()
                print("Logout with status: %s" % status)

# Handle SIGTERM signal when docker stops the current container
def receive_termination_signal(signum, frame):
    global is_running
    is_running = False
    print('!!! SIGTERM signal received !!!')

if __name__ == '__main__':
    # Handle SIGTERM signal
    signal.signal(signal.SIGTERM, receive_termination_signal)  

    # Specify model from arguments
    args = sys.argv
    if len(args) > 1:
        model_name = str(args[1]).lower()
        print('Specified model = {}' .format(model_name))
    else:
        model_name = default_model

    # Copy result.html to /data/misc/qmmf
    shutil.copy('result.html', 'output/result.html')

    # Start main()
    main(IOT_HUB_PROTOCOL)
