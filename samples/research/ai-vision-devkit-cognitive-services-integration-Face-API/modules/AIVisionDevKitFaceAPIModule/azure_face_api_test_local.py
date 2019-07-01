# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import requests
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import os
import webbrowser
import base64
import json
from matplotlib import font_manager as fm, rcParams


camera_ip = os.environ['CAMERA_IP']
subscription_key = os.environ['FACE_API_SUBSCRIPTION_KEY']
face_api_url = os.environ['FACE_API_URL']


# start camera
camera_session = requests.session()
camera_base_url = 'http://' + camera_ip + ':4000'
camera_headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
        }
url = camera_base_url + '/connect'
payload = {}
camera_response = camera_session.post(url, headers=camera_headers, data=payload)
camera_response.raise_for_status()

url = camera_base_url + '/startcamera'
payload = {
        'camera_id': 0,
        'flags': 0,
        'zsl_mode': 0,
        'zsl_queue_depth': 8,
        'zsl_width': 1920,
        'zsl_height': 1080,
        'framerate': 30
        }
camera_response = camera_session.post(url, headers=camera_headers, data=payload)
camera_response.raise_for_status()

url = camera_base_url + '/createsession'
payload = {}
camera_response = camera_session.post(url, headers=camera_headers, data=payload)
camera_response.raise_for_status()

url = camera_base_url + '/createvideotrack'
payload = {
        'camera_id': 0,
        'track_id': 1,
        'session_id': 1,
        'track_width': 1920,
        'track_height': 1080,
        'track_codec': 1,
        'bitrate': 10000000,
        'framerate': 30,
        'track_output': 0,
        'low_power_mode': 0
        }
camera_response = camera_session.post(url, headers=camera_headers, data=payload)
camera_response.raise_for_status()

url = camera_base_url + '/startsession'
payload = {'session_id': 1}
camera_response = camera_session.post(url, headers=camera_headers, data=payload)
camera_response.raise_for_status()

# take snapshot with camera
url = camera_base_url + '/captureimage'
payload = {'camera_id': 0, 'image_width': 1920, 'image_height': 1080, 'image_quality': 100}
camera_response = camera_session.post(url, headers=camera_headers, data=payload)
camera_response.raise_for_status()
image_data = base64.b64decode(camera_response.json()["Data"])

# stop camera


# send snapshot to Azure Face API
headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': subscription_key
        }
params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
        'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
        }
detect_face_api_url = face_api_url + '/face/v1.0/detect'
face_api_response = requests.post(detect_face_api_url,
                                  params=params, headers=headers, data=image_data)
face_api_response.raise_for_status()
faces = face_api_response.json()


# Display the original image and overlay it with the face information.
source_img = Image.open(BytesIO(image_data))

fontpath = os.path.join(rcParams["datapath"], "fonts/ttf/DejaVuSansMono.ttf")
font = ImageFont.truetype(fontpath, 84)
for face in faces:
    draw = ImageDraw.Draw(source_img)
    fr = face["faceRectangle"]
    fa = face["faceAttributes"]
    origin = (fr["left"], fr["top"])
    size = (fr["width"], fr["height"])
    coordinates = (origin[0], origin[1], origin[0] + size[0], origin[1] + size[1])
    label = "%s, %s" % (fa["gender"].capitalize(), fa["glasses"])
    draw.rectangle(coordinates, outline="blue", width=4)
    draw.text((coordinates[0], coordinates[3]), label, fill='white', font=font)

source_img.save('Azure_Face_Api_Result.jpg', "JPEG")
source_img.show()
with open('Azure_Face_Api_Result.json', 'w') as outfile:
    json.dump(faces, outfile, indent=4)
# print(json.dumps(faces, indent=4))
webbrowser.open('file://' + os.path.realpath('Azure_Face_Api_Result.json'))
