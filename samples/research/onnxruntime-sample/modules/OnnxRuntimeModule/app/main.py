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
enable_iot = True

# Define constants
is_busy = False
new_frame = []

model_file = "tiny_yolov2/model.onnx"

threshold = 0.5

numClasses = 20
labels = ["aeroplane","bicycle","bird","boat","bottle",
          "bus","car","cat","chair","cow","dining table",
          "dog","horse","motorbike","person","potted plant",
          "sheep","sofa","train","tv monitor"]
    
colors = [(255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),
          (255,255,0),(0,255,255),(255,0,255),(128,128,0),(0,128,128),(128,0,128),
          (255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),
          (255,64,64),(64,255,64)]
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

def sigmoid(x, derivative=False):
  return x*(1-x) if derivative else 1/(1+np.exp(-x))

def softmax(x):
  scoreMatExp = np.exp(np.asarray(x))
  return scoreMatExp / scoreMatExp.sum(0)

def draw_bboxes(out, image, duration):
    global threshold
    global numClasses
    global labels
    global colors
    global anchors
    global iot_hub_manager

    for cy in range(0,13):
        for cx in range(0,13):
            for b in range(0,5):
                channel = b*(numClasses+5)
                tx = out[channel  ][cy][cx]
                ty = out[channel+1][cy][cx]
                tw = out[channel+2][cy][cx]
                th = out[channel+3][cy][cx]
                tc = out[channel+4][cy][cx]
                x = (float(cx) + sigmoid(tx))*32
                y = (float(cy) + sigmoid(ty))*32
   
                w = np.exp(tw) * 32 * anchors[2*b  ]
                h = np.exp(th) * 32 * anchors[2*b+1] 
   
                confidence = sigmoid(tc)

                classes = np.zeros(numClasses)
                for c in range(0,numClasses):
                    classes[c] = out[channel + 5 + c][cy][cx]
                classes = softmax(classes)
                class_index = classes.argmax()
                
                if (classes[class_index] * confidence < threshold):
                    continue

                color = colors[class_index]
                x = x - w/2
                y = y - h/2

                # draw BBOX on the original image
                Width = image.shape[1]
                Height = image.shape[0]
                scale = max(Width, Height)
                
                x = x * scale / 416 - (scale - Width) / 2
                y = y * scale / 416 - (scale - Height) / 2
                w = w * scale / 416
                h = h * scale / 416

                x1 = max(int(np.round(x)), 0)
                y1 = max(int(np.round(y)), 0)
                x2 = min(int(np.round(x + w)), Width)
                y2 = min(int(np.round(y + h)), Height)
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                #print('x1, y1, x2, y2 = {}, {}, {}, {}' .format(x1, y1, x2, y2))

                # write label
                cv2.rectangle(image, (x1, y1 - 40), (x1 + 200, y1), color, -1)
                cv2.putText(image, labels[class_index], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255 - color[0], 255 - color[1], 255 - color[2]), 1, cv2.LINE_AA)
    
                if enable_iot:
                    # Send message to IoT Hub
                    message = {
                        "Label": labels[class_index],
                        "Confidence": str(confidence),
                        "BBox": [x1, y1, x2, y2],
                        "TimeStamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    }
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

def detect_image(session, input_name):
    global is_busy
    global new_frame
    global is_running

    while (is_running):

        try:
            if (len(new_frame) == 0):
                #print('New frame not ready!')
                time.sleep(0.1)
                continue

            image = new_frame
            new_frame = []

            resized_image = resize_and_pad(image, 416, 416)
            input_data = np.ascontiguousarray(np.array(resized_image, dtype=np.float32).transpose(2, 0, 1)) # BGR => RGB
            input_data = np.expand_dims(input_data, axis=0)

            start_time = time.time()
            result = session.run(None, {input_name: input_data})
            end_time = time.time()
            duration = end_time - start_time  # sec

            out = result[0][0]
            draw_bboxes(out, image, duration)

        except Exception as ex:
            print("Exception in detect_image: %s" % ex)
            time.sleep(0.1)

        is_busy = False

def detect_camera(preview_url):
    global is_busy
    global new_frame
    global model_file
    global is_running

    # Load model
    session = rt.InferenceSession(model_file)        
    input_name = session.get_inputs()[0].name
    print('\ninput node name = {}' .format(input_name))

    shutil.copy('result.html', 'output/result.html')

    # Start a thread to detect a captured frame    
    threading.Thread(target=detect_image, daemon=True, args=(session, input_name)).start()

    # Read rtsp stream and detect each frame

    # Note: Current OpenCV VideoCapture() has memory leak for reading RTST Steam:
    #       If your application is actual a little bit slower than your configured fps you got a memory leak.
    #       https://github.com/opencv/opencv/issues/5715
    
    while (is_running):
        new_frame = []
        has_frame = False
        is_busy = False

        cap = cv2.VideoCapture(preview_url)
        time.sleep(1)

        # Capture frame-by-frame
        while (is_running and cap.isOpened() == True):
            try:
                if is_busy:
                    has_frame = cap.grab()  # don't retrieve frame if the previous frame processing hadn't finished
                else:
                    has_frame, frame = cap.read()
                    if (has_frame)                                     :
                        new_frame = frame
                        is_busy = True

                # If WiFi connection speed is slow, cv2.VideoCapture(preview_url) will fail to capture frame frequently
                if not has_frame: 
                    new_frame = []
                    print("No frame!  Restart cv2.VideoCapture()!  ")
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
