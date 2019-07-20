# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import cv2
import urllib.request
import sys
import numpy as np

is_recording = False
is_yolov3 = False

image_file = "result.jpg"
video_file = "result.mp4"

video_width = 960
video_heigth = 540

if is_yolov3:
    wait_time = 3000  # ms
    video_fps = 1
else:
    wait_time = 500  # ms
    video_fps = 2

def main():    
    img_url = None
    input_args = sys.argv

    if len(input_args) > 1:
        img_url = input_args[1]
    else:
        print('Require to input image url: "http://<camera_ip>:1080/media/result.jpg"')
        print('For example: python show_result.py "http://192.168.0.2:1080/media/result.jpg"')
        return

    if is_recording:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_file, fourcc, video_fps, (video_width, video_heigth))
        
    while True:
        try:  
            #urllib.request.urlretrieve(img_url, image_file)
            #img = cv2.imread(image_file)

            #height, width = img.shape[:2]
            #height = int(height * 0.5)
            #width = int(width * 0.5)
            #img = cv2.resize(img, (width, height))

            req = urllib.request.urlopen(img_url)
            data = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR) 

            if is_recording:
                out.write(img)
            cv2.imshow("Detect " + image_file, img)
            
            img = None
        except Exception as ex:
            print('Exception for reading image: {}' .format(ex))

        if (cv2.waitKey(wait_time) & 0xFF) == ord('q'):
            break

    if is_recording:
        out.release()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()