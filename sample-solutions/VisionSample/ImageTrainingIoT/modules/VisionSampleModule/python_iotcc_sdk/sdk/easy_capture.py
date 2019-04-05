import argparse
import sys, os, zipfile, shutil
import time

class Easy_Capture(object):
    def __init__(self, camera, folder, prefix):
        # default picture folder at CURRENT_DIR/pictures/
        # default configure is 'usb control'
        self.CURRENT_FOLDER = os.getcwd()
        self.IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__name__)), folder)
        self.CAMERA = camera
        self.tag = prefix

    def capture(self, nums=5, delay=5):
        if self.CAMERA is None:
            return False
        print("Start capture images: " + str(nums))
        for t in range(delay):
            self.CAMERA.set_overlay_state("off")
            curr_t = delay - t;
            self.CAMERA.configure_overlay("text", self.tag + " images in " + str(curr_t) + " sec")
            self.CAMERA.set_overlay_state("on")
            time.sleep(1)
        self.CAMERA.set_overlay_state("off")
        self.CAMERA.configure_overlay("text", self.tag + " images shooting ...")
        self.CAMERA.set_overlay_state("on")
        for x in range(nums):
            if self.CAMERA.captureImageWithFolder(self.IMAGES_FOLDER, self.tag):
                print("capture well and image index:" + str(x))
            else:
                print("image capture error and image index:" + str(x))
        print("capture end!")
        time.sleep(1)
        self.CAMERA.set_overlay_state("off")
        return True
