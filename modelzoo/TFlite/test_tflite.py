# -*- codin#%%
import numpy as np
import tensorflow as tf
import cv2

#%%
model_path = "/home/boris/exported/ssd_mobilenet_v1_coco_2018_01_28/ssd_graph.tflite"
input_file = "/home/boris/dog.jpg"

img = cv2.imread(input_file)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = cv2.resize(img, (300, 300)).astype(np.float32)
img = img * 1./128. - 1
img = np.expand_dims(img, axis=0)

# Load TFLite model and allocate tensors.
interpreter = tf.contrib.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

#%%
# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

#%%
# Test model on random input data.
input_shape = input_details[0]['shape']
input_data = img #np.array(np.random.random_sample(input_shape), dtype=np.float32)
interpreter.set_tensor(input_details[0]['index'], input_data)

#%%
interpreter.invoke()

boxes = interpreter.get_tensor(output_details[0]['index']).squeeze(0)
classes = interpreter.get_tensor(output_details[1]['index']).squeeze(0)
scores = interpreter.get_tensor(output_details[2]['index']).squeeze(0)

num = interpreter.get_tensor(output_details[3]['index']).astype(int)[0]