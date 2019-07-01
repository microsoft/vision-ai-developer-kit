# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import requests
from PIL import Image, ImageFile, ImageFont, ImageDraw
import os
import json
from pathlib import Path
from . iot_hub_manager import IotHubManager
from iotccsdk import CameraClient

subscription_key = os.environ['FACE_API_SUBSCRIPTION_KEY']
face_api_url = os.environ['FACE_API_URL']
dir_name = os.path.dirname(os.path.abspath(__name__))
file_name = "qmmf_snapshot*.jpg"
# remove_file_name_type1 = "snapshot*.jpg"
# remove_file_name_type2 = "qmmf_snapshot*.jpg"
remove_file_name = "*napshot*.jpg"


def remove_old_snapshots(dir_name, remove_file_name):
    snapshot_files = list(Path(dir_name).glob("**/%s" % remove_file_name))
    for file in snapshot_files:
        str_file = str(file)
        os.chmod(str_file, 0o777)
        os.remove(str_file)


def get_snapshot_name(file_name=file_name):
    selected_files = list(Path(dir_name).glob("**/%s" % file_name))

    if len(selected_files) != 1:
        print("Expected 1 file but got %s" %
              (selected_files))
        return

    str_file = str(selected_files[0])
    print(str_file)
    os.chmod(str_file, 0o777)
    return str_file


def azure_face_api_detect(camera_client=None, iot_hub_manager=None):
    # sends snapshot to azure face api to detect faces and features
    remove_old_snapshots(dir_name, file_name)
    camera_client.captureimage()

    detect_face_api_url = face_api_url + '/face/v1.0/detect'

    headers = {'Content-Type': 'application/octet-stream',
               'Ocp-Apim-Subscription-Key': subscription_key}
    params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
            'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
    }

    image_data = open(get_snapshot_name(), "rb")
    response = requests.post(detect_face_api_url, params=params, headers=headers, data=image_data)
    response.raise_for_status()
    faces = response.json()

    # Open the original image and overlay it with the face information.
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    source_img = Image.open(image_data)

    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 84)
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

    if len(faces) > 0:
        source_img.save('/app/host_image_folder/Azure_Face_Api_Result.jpg', "JPEG")
        with open('/app/host_image_folder/Azure_Face_Api_Result.json', 'w') as outfile:
            json.dump(faces, outfile, indent=4)
        iot_hub_manager.send_message_to_upstream(json.dumps(faces, indent=4))
        print(json.dumps(faces, indent=4))
        return True
    else:
        return False
