# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import threading
import numpy as np
import onnxruntime as rt
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

# Handle SIGTERM signal when docker stops the current VisionSampleModule container
import signal
is_running = True

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
IOT_HUB_PROTOCOL = IoTHubTransportProvider.MQTT

iot_hub_manager = None

# Disable iotedge for pure docker run
enable_iot = False

# Define constants
new_frame = []

model_file = "yolov3/yolov3.onnx"

threshold = 0.5

numClasses = 80
labels = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat", "traffic light", 
          "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", 
          "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", 
          "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", 
          "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", 
          "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed", 
          "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", 
          "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
         ]
colors = [(255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),(255,255,0),(0,255,255),(255,0,255),(128,128,0),
          (0,128,128),(128,0,128),(255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),(255,64,64),(64,255,64),
          (255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),(255,255,0),(0,255,255),(255,0,255),(128,128,0),
          (0,128,128),(128,0,128),(255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),(255,64,64),(64,255,64),
          (255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),(255,255,0),(0,255,255),(255,0,255),(128,128,0),
          (0,128,128),(128,0,128),(255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),(255,64,64),(64,255,64),
          (255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),(255,255,0),(0,255,255),(255,0,255),(128,128,0),
          (0,128,128),(128,0,128),(255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),(255,64,64),(64,255,64)
          ]

anchors = [1.08, 1.19, 3.42, 4.41, 6.63, 11.38, 9.42, 5.11, 16.62, 10.52]


def resize_and_pad(img, width, height, pad_value=114):
    
    img_height, img_width = img.shape[:2]

    scale_w = 1.0 if (img_width >= img_height) else float(img_width / img_height)
    scale_h = 1.0 if (img_height >= img_width) else float(img_height / img_width)

    target_w = int(float(width) * scale_w)
    target_h = int(float(height) * scale_h)

    resized = cv2.resize(img, (target_w, target_h), 0, 0, interpolation=cv2.INTER_NEAREST)

    top = int(max(0, np.round((height - target_h) / 2)))
    left = int(max(0, np.round((width - target_w) / 2)))
    bottom = height - top - target_h
    right = width - left - target_w
    resized_with_pad = cv2.copyMakeBorder(resized, top, bottom, left, right,
                                          cv2.BORDER_CONSTANT, value=[pad_value, pad_value, pad_value])

    return resized_with_pad

def draw_bboxes(result, image, duration):

    out_boxes, out_scores, out_classes = result[:3]
    #print('out_classes = {}, {}' .format(len(out_classes), out_classes))

    for i in range(len(out_classes)):
        batch_index, class_index, box_index = out_classes[i][:3]
        confidence = out_scores[batch_index][class_index][box_index]
        if confidence >= threshold:
            y1, x1, y2, x2 = out_boxes[batch_index][box_index]

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            color = colors[class_index]
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

            # write label
            cv2.rectangle(image, (x1, y1 - 40), (x1 + 200, y1), color, -1)
            cv2.putText(image, labels[class_index], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255 - color[0], 255 - color[1], 255 - color[2]), 1, cv2.LINE_AA)

            message = { "Label": labels[class_index],
                        "Confidence": str(confidence),
                        "BBox": [x1, y1, x2, y2],
                        "TimeStamp": str(datetime.datetime.utcnow())
                       }
            print('detection result: {}' .format(json.dumps(message)))
            if enable_iot:
                # Send message to IoT Hub                
                iot_hub_manager.send_message_to_upstream(json.dumps(message))

    # Write detection time        
    fps = 1.0 / duration
    text = "Detect 1 frame : {:8.6f} sec | {:6.2f} fps" .format(duration, fps)
    cv2.putText(image, text, (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)

    # Reduce image size to speed up image saving
    height, width = image.shape[:2]
    height = int(height * 0.5)
    width = int(width * 0.5)
    image = cv2.resize(image, (width, height))
    cv2.imwrite("output/result.jpg", image)
    image = None

def detect_image(session, input_name, input_size):
    global new_frame
    global is_running

    while (is_running):

        try:
            if (len(new_frame) == 0):
                #print('New frame not ready!')
                time.sleep(0.1)
                continue

            image = new_frame

            resized_image = resize_and_pad(image, 416, 416)
            image_data = np.ascontiguousarray(np.array(resized_image, dtype=np.float32).transpose(2, 0, 1)) # BGR => RGB
            image_data /= 255.
            image_data = np.expand_dims(image_data, axis=0)
            
            image_size = np.array([image.shape[0], image.shape[1]], dtype=np.int).reshape(1, 2)

            start_time = time.time()
            result = session.run(None, {input_name.name: image_data, input_size.name: image_size})
            end_time = time.time()
            duration = end_time - start_time  # sec
            
            draw_bboxes(result, image, duration)

        except Exception as ex:
            print("Exception in detect_image: %s" % ex)
            time.sleep(0.1)

        new_frame = []

def detect_camera(preview_url):
    global new_frame
    global model_file
    global is_running

    # Load model
    session = rt.InferenceSession(model_file)        
    input_name, input_size = session.get_inputs()[:2]
    print('\ninput nodes = {}, {}' .format(input_name.name, input_size.name))

    shutil.copy('result.html', 'output/result.html')

    # Start a thread to detect a captured frame    
    threading.Thread(target=detect_image, daemon=True, args=(session, input_name, input_size)).start()

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
                if len(new_frame) > 0:  # detect_image() thread hand't finished to detect the latest frame
                    has_frame = cap.grab()  # don't retrieve frame if the previous frame processing hadn't finished
                else:
                    has_frame, frame = cap.read()
                    if (has_frame)                                     :
                        new_frame = frame

                # If WiFi connection speed is slow, cv2.VideoCapture(preview_url) will fail to capture frame frequently
                if not has_frame: 
                    new_frame = []
                    print("No frame!  Restart cv2.VideoCapture()!")
                    print("TimeStamp: {}" .format(datetime.datetime.utcnow()))
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
            if (enable_iot):
                iot_hub_manager = IotHubManager(protocol, camera_client)

            print('supported resolutions: ' + str(camera_client.resolutions))
            print('supported encodetype: ' + str(camera_client.encodetype))
            print('supported bitrates: ' + str(camera_client.bitrates))
            print('supported framerates: ' + str(camera_client.framerates))
            print(camera_client.configure_preview(resolution="1080P", framerate=24, display_out=1))

            camera_client.set_preview_state("on")

            preview_url = camera_client.preview_url
            print('preview_url = {}' .format(preview_url))

            if (enable_iot):
                # Write rtsp_addr to twin
                print ( "Sending rtsp_addr property..." )
                prop = {"rtsp_addr": preview_url}
                prop = json.dumps(prop)            
                iot_hub_manager.send_property(prop)

            preview_url = "rtsp://localhost:8900/live"  # comment it if running by pure docker run
            detect_camera(preview_url)

        except IoTHubError as iothub_error:
            print("Unexpected error %s from IoTHub" % iothub_error)
            return
        
        except KeyboardInterrupt:
            print("IoTHubModuleClient sample stopped")
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
    signal.signal(signal.SIGTERM, receive_termination_signal)  # Handle SIGTERM signal
    main(IOT_HUB_PROTOCOL)
