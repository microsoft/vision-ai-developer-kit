# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import numpy as np
import onnxruntime as rt
import cv2
import time
import datetime
import sys
import json

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

def draw_object(image, color, label, confidence, x1, y1, x2, y2, enable_iot, iot_hub_manager):
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    cv2.rectangle(image, (x1, y1 - 40), (x1 + 200, y1), color, -1)
    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255 - color[0], 255 - color[1], 255 - color[2]), 1, cv2.LINE_AA)

    message = { "Label": label,
                "Confidence": "{:6.4f}".format(confidence),
                "Position": [x1, y1, x2, y2],
                "TimeStamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
              }
    print('detection result: {}' .format(json.dumps(message)))
    if enable_iot:
        # Send message to IoT Hub                    
        iot_hub_manager.send_message_to_upstream(json.dumps(message))

def output_result(image, duration):
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

class TinyYOLOv2Class():
    def __init__(self, iot_hub_manager, enable_iot):
        self.model_file = 'tiny_yolov2/model.onnx'
        self.threshold = 0.4
        self.numClasses = 20
        self.labels = ["aeroplane","bicycle","bird","boat","bottle",
                       "bus","car","cat","chair","cow","dining table",
                       "dog","horse","motorbike","person","potted plant",
                       "sheep","sofa","train","tv monitor"
                      ]
        self.colors = [(255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),
                       (255,255,0),(0,255,255),(255,0,255),(128,128,0),(0,128,128),(128,0,128),
                       (255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),
                       (255,64,64),(64,255,64)
                      ]
        self.anchors = [1.08, 1.19, 3.42, 4.41, 6.63, 11.38, 9.42, 5.11, 16.62, 10.52]

        self.iot_hub_manager = iot_hub_manager
        self.enable_iot = enable_iot

        # Load model
        self.session = rt.InferenceSession(self.model_file)        
        self.inputs = self.session.get_inputs()

    def draw_bboxes(self, result, image, duration):
        out = result[0][0]
        for cy in range(0,13):
            for cx in range(0,13):
                for b in range(0,5):
                    channel = b*(self.numClasses+5)
                    tx = out[channel  ][cy][cx]
                    ty = out[channel+1][cy][cx]
                    tw = out[channel+2][cy][cx]
                    th = out[channel+3][cy][cx]
                    tc = out[channel+4][cy][cx]
                    x = (float(cx) + sigmoid(tx))*32
                    y = (float(cy) + sigmoid(ty))*32
   
                    w = np.exp(tw) * 32 * self.anchors[2*b  ]
                    h = np.exp(th) * 32 * self.anchors[2*b+1] 
   
                    confidence = sigmoid(tc)

                    classes = np.zeros(self.numClasses)
                    for c in range(0, self.numClasses):
                        classes[c] = out[channel + 5 + c][cy][cx]
                    classes = softmax(classes)
                    class_index = classes.argmax()
                
                    if (classes[class_index] * confidence < self.threshold):
                        continue

                    x = x - w/2
                    y = y - h/2

                    # draw BBOX on the original image
                    image_h, image_w = image.shape[:2]
                    scale = max(image_w, image_h)
                
                    x = x * scale / 416 - (scale - image_w) / 2
                    y = y * scale / 416 - (scale - image_h) / 2
                    w = w * scale / 416
                    h = h * scale / 416

                    x1 = max(int(np.round(x)), 0)
                    y1 = max(int(np.round(y)), 0)
                    x2 = min(int(np.round(x + w)), image_w)
                    y2 = min(int(np.round(y + h)), image_h)

                    # Draw labels and bbox and output message
                    draw_object(image, self.colors[class_index], self.labels[class_index], confidence, 
                                x1, y1, x2, y2, self.enable_iot, self.iot_hub_manager)

        # Output detection result
        output_result(image, duration)
        image = None

    def detect_image(self, image):
        try:
            # Preprocess input image
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR => RGB
            img = resize_and_pad(img, 416, 416)
            image_data = np.ascontiguousarray(np.array(img, dtype=np.float32).transpose(2, 0, 1)) # HWC -> CHW
            image_data = np.expand_dims(image_data, axis=0)

            # Detect image
            start_time = time.time()
            result = self.session.run(None, {self.inputs[0].name: image_data})
            end_time = time.time()
            duration = end_time - start_time  # sec
            
            # Output detection result
            self.draw_bboxes(result, image, duration)

        except Exception as ex:
            print("Exception in detect_image: %s" % ex)
            time.sleep(0.1)

        img = None
        image_data = None

class YOLOV3Class():
    def __init__(self, iot_hub_manager, enable_iot):
        self.model_file = 'yolov3/yolov3.onnx'
        self.threshold = 0.5
        self.numClasses = 80
        self.labels = [ "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat", "traffic light", 
                        "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", 
                        "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", 
                        "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", 
                        "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", 
                        "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed", 
                        "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", 
                        "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
                       ]
        self.colors = [ (255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),(255,255,0),(0,255,255),(255,0,255),(128,128,0),
                        (0,128,128),(128,0,128),(255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),(255,64,64),(64,255,64),
                        (255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),(255,255,0),(0,255,255),(255,0,255),(128,128,0),
                        (0,128,128),(128,0,128),(255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),(255,64,64),(64,255,64),
                        (255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),(255,255,0),(0,255,255),(255,0,255),(128,128,0),
                        (0,128,128),(128,0,128),(255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),(255,64,64),(64,255,64),
                        (255,0,0),(0,255,0),(0,0,255),(128,0,0),(0,128,0),(0,0,128),(255,255,0),(0,255,255),(255,0,255),(128,128,0),
                        (0,128,128),(128,0,128),(255,128,128),(128,255,128),(128,128,255),(128,64,64),(64,128,64),(64,64,128),(255,64,64),(64,255,64)
                       ]
        self.anchors = [1.08, 1.19, 3.42, 4.41, 6.63, 11.38, 9.42, 5.11, 16.62, 10.52]

        self.iot_hub_manager = iot_hub_manager
        self.enable_iot = enable_iot

        # Load model
        self.session = rt.InferenceSession(self.model_file)        
        self.inputs = self.session.get_inputs()

    def draw_bboxes(self, result, image, duration):
        out_boxes, out_scores, out_classes = result[:3]
        image_h, image_w = image.shape[:2]
        for i in range(len(out_classes)):
            batch_index, class_index, box_index = out_classes[i][:3]
            confidence = out_scores[batch_index][class_index][box_index]
            if confidence >= self.threshold:
                y1, x1, y2, x2 = out_boxes[batch_index][box_index]

                x1 = max(int(np.round(x1)), 0)
                y1 = max(int(np.round(y1)), 0)
                x2 = min(int(np.round(x2)), image_w)
                y2 = min(int(np.round(y2)), image_h)

                # Draw labels and bbox and output message
                draw_object(image, self.colors[class_index], self.labels[class_index], confidence, 
                            x1, y1, x2, y2, self.enable_iot, self.iot_hub_manager)

        # Output detection result
        output_result(image, duration)
        image = None

    def detect_image(self, image):
        try:
            # Preprocess input image
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR => RGB
            img = resize_and_pad(img, 416, 416)
            image_data = np.ascontiguousarray(np.array(img, dtype=np.float32).transpose(2, 0, 1)) # BGR => RGB
            image_data /= 255.
            image_data = np.expand_dims(image_data, axis=0)

            image_size = np.array([image.shape[0], image.shape[1]], dtype=np.int32).reshape(1, 2)

            # Detect image
            start_time = time.time()
            result = self.session.run(None, {self.inputs[0].name: image_data, self.inputs[1].name: image_size})
            end_time = time.time()
            duration = end_time - start_time  # sec
            
            # Ouput detection result
            self.draw_bboxes(result, image, duration)

        except Exception as ex:
            print("Exception in detect_image: %s" % ex)
            time.sleep(0.1)

        img = None
        image_data = None