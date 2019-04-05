# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

import argparse
import sys, os, shutil
import time
import subprocess
import utility
import iot
from camera import CameraClient
from easy_capture import Easy_Capture
from training_images import Train_Images

if sys.version_info >= (3, 6):
    import zipfile
else:
    import zipfile36 as zipfile


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "y")


def main():
    print("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--var', type=str,
                            dest='var',
                            help='variables with isPush, tags and number of images to capture ',
                            default='True')
    parser.add_argument('-t', '--tag', type=str, nargs='+',
                            dest='tag',
                            help='image tag name',
                            default='Orange')
    parser.add_argument('-n', '--num', type=int, dest='num', help='number of images to capture ', default = 5)
    parser.add_argument('--ip', help='ip address of the camera', default=utility.getWlanIp())
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    if args.var is not None:
        vlist = [str(c) for c in args.var]
        #vars = vlist[0].split()
        c_len = len(vlist)
        print("args.var length: " + str(c_len))
    if args.tag is not None:
        taglist = [str(t1) for t1 in args.tag]
        tags = taglist[0].split()
        tag_len = len(tags)
        print("tag length:" + str(tag_len) + " tags: " + tags[0])
    if args.num is not None:
        num = args.num
        print("num: "+ str(num))
    ip_addr = args.ip
    username = args.username
    password = args.password
    mypushmodel = True #str2bool(vars[0])

    # getting Iot hub sdk ready with hub manager
    hub_manager = iot.HubManager()

    # Connecting to camer using ipcWebServer SDK and turing camera on and then starting inferencing
    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        # this call we set the camera to display over HDMI
        print(camera_client.configure_preview(resolution="1080P", display_out=1))
        # this call turns on the camera and start transmetting over RTSP and HDMI a stream from camera
        camera_client.set_preview_state("on")

        # rtsp stream address
        rtsp_stream_addr = str(camera_client.preview_url)
        print("rtsp stream is :: " + rtsp_stream_addr)
        # uploading rtsp stream address to iot hub as twin property so that user one can know what
        # there rtsp address is and then use it on vlc media player
        hub_manager.iothub_client_sample_run(rtsp_stream_addr)
        dirpath = os.getcwd()
        # MODEL_FOLDER = os.path.join(dirpath,"model")
        # if not os.path.exists(MODEL_FOLDER):
        #    os.makedirs(MODEL_FOLDER)
        MODEL_FOLDER = os.path.dirname(os.path.abspath('/app/vam_model_folder'))
        model_dlc = os.path.join(MODEL_FOLDER, "model.dlc")
        # transferring model files to camera for inferencing
        if os.path.exists(model_dlc) is not True:
            print("Not transferring dlc  as per parameter passed")
            background = Easy_Capture(camera_client, folder='pictures', prefix='background')
            n=num
            background.capture(nums=n)
            loops = tag_len
            for i in range(loops):
                object = Easy_Capture(camera_client, folder='pictures', prefix=tags[0])
                object.capture(nums=n)
            camera_client.configure_overlay("text", "Training ...")
            camera_client.set_overlay_state("on")
            time.sleep(2)
            trainer = Train_Images()
            trainer.train_project()
            camera_client.set_overlay_state("off")
            camera_client.configure_overlay("text", "Training done! Move files ...")
            camera_client.set_overlay_state("on")
            if not os.path.isfile(trainer.CUSTOMVISION_PROJECT_NAME + ".zip"):
                print("trained model file not found")
                return False
            zip_ref = zipfile.ZipFile(os.path.abspath(trainer.CUSTOMVISION_PROJECT_NAME + ".zip"))
            zip_ref.extractall(MODEL_FOLDER)
            zip_ref.close()
            time.sleep(10)
            prototxt = os.path.join(MODEL_FOLDER, "model.prototxt")
            if os.path.exists(prototxt):
                os.remove(prototxt)
                print("*** model.prototxt removed ***")
            shutil.rmtree("pictures")
            # os.unlink(trainer.CUSTOMVISION_PROJECT_NAME + ".zip")
            time.sleep(10)

        utility.transfervam()
        camera_client.set_overlay_state("off")
        camera_client.set_preview_state("off")
        camera_client.configure_preview(resolution="1080P", display_out=1)
        time.sleep(5)
        camera_client.set_preview_state("on")
        camera_client.set_overlay_state("off")
        camera_client.configure_overlay("text", "inference")
        camera_client.set_overlay_state("on")
        # Vam(Video analytics engine ) this will take the model and run on the device
        camera_client.set_analytics_state("on")
        print(camera_client.vam_url)

        # this will set the frames to be overlayed with information received from inference results from your model
        camera_client.configure_overlay("inference")

        #Turning overlay to Truse to see inferencing frame overlayed with inference results
        camera_client.set_overlay_state("on")

        # we will use gstreamer to get the inference results from camera into this module and then send them up to cloud or another module
        try:
            with camera_client.get_inferences() as results:
                print_inferences(results, camera_client, hub_manager)
        except KeyboardInterrupt:
            print("Stopping")
        try:
            print("inside infinite loop now")
            while(True):
                time.sleep(2)
        except KeyboardInterrupt:
            print("Stopping")

        # turning everything off and logging out ...
        camera_client.set_overlay_state("off")
        camera_client.set_analytics_state("off")
        camera_client.set_preview_state("off")


def print_inferences(results=None, camera_client=None, hub_manager=None):
        for result in results:
            if result is not None and result.objects is not None and len(result.objects):
                timestamp = result.timestamp
                if timestamp:
                    print("timestamp={}".format(timestamp))
                else:
                    print("timestamp= " + "None")
                for object in result.objects:
                    id = object.id
                    print("id={}".format(id))
                    label = object.label
                    print("label={}".format(label))
                    confidence = object.confidence
                    print("confidence={}".format(confidence))
                    x = object.position.x
                    y = object.position.y
                    w = object.position.width
                    h = object.position.height
                    print("Position(x,y,w,h)=({},{},{},{})".format(x, y, w, h))
                    hub_manager.SendMsgToCloud("I see " + str(label) + " with confidence :: " + str(confidence))
                    print("")
            else:
                print("No results")

if __name__ == '__main__':
    main()
