# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import cv2
import urllib.request
import sys

def main():    
    img_url = None
    input_args = sys.argv

    if len(input_args) > 1:
        img_url = input_args[1]
    else:
        print('Require to input image url: "http://<camera_ip>:1080/media/result.jpg"')
        print('For example: python show_result.py "http://192.168.0.2:1080/media/result.jpg"')
        return

    while True:
        try:  
            urllib.request.urlretrieve(img_url, "result.jpg")
            img = cv2.imread("result.jpg")
            #height, width = img.shape[:2]
            #height = int(height * 0.5)
            #width = int(width * 0.5)
            #img = cv2.resize(img, (width, height))
            cv2.imshow("result.jpg",img)
            img = None
        except:
            print('Fail to read image!')

        if cv2.waitKey(200) & 0xFF == ord('q'):
            break
        
    cv2.destroyAllWindows()
    cap.release()

if __name__ == '__main__':
    main()