# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import threading
import cv2
import time
import datetime
import sys
import json
from getmodel import TinyYOLOv2Class, YOLOV3Class, FasterRCNNClass, EmotionClass

# Define model map
model_map = {
    'tinyyolov2': TinyYOLOv2Class,
    'yolov3': YOLOV3Class,
    'fasterrcnn': FasterRCNNClass, 
    'emotion': EmotionClass
}

default_model = 'tinyyolov2'
#default_model = 'yolov3'
#default_model = 'fasterrcnn'
#default_model = 'emotion'

model_name = default_model
model_class = None

preview_url = "rtsp://<camera_ip>:8900/live"   # replace <camera_ip> to your camera device ip

is_running = True
is_busy = False

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

        if (cv2.waitKey(1)) > 0:
            is_running = False

def capture_frames(preview_url):
    global new_frame
    global model_class
    global is_busy

    # Get model_class 
    if model_name in model_map:
        model_class = model_map[model_name]()
    else:
        model_class = model_map[default_model]()

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

def main():
    # Start to detect object
    capture_frames(preview_url)

if __name__ == '__main__':

    # Specify model from arguments
    args = sys.argv
    if len(args) > 1:
        model_name = str(args[1]).lower()
        print('Specified model = {}' .format(model_name))
    else:
        model_name = default_model

    # Start main()
    main()
