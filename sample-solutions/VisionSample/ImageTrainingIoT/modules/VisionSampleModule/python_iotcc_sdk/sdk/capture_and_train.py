import argparse
import sys, os, zipfile, shutil
import time

from camera import CameraClient
from training_images import Train_Images
import utility

def capture(camera, nums, tag):
        time.sleep(1)

        print("Start capture images: " + str(nums))
        for x in range(nums):
            if camera.captureImageWithFolder('pictures', tag):
                print("capture well and image index:" + str(x))
            else:
                print("image capture error and image index:" + str(x))
        print("capture end!")
        time.sleep(1)

def capture_train():
    print("\nPython %s\n" % sys.version)
    CURRENT_FOLDER = os.getcwd()
    MODEL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__name__)), "model")
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tags', nargs='+', type=str, dest='tags', action='append', help='please input tag name')
    parser.add_argument('-n', '--nums', nargs='+', type=int, dest='nums', action='append', help='please input numbers of images to capture')
    parser.add_argument('-p','--pushmodel', help ='sets whether to push the model and required files to device or not', default=True)
    parser.add_argument('--ip', help='ip address of the camera', default=utility.getWlanIp())
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    num1 = 5
    tag1 = 'Orange'
    array_len = 1
    mypushmodel = True
    if args.tags is not None:
        tags = [str(tag) for tag in args.tags]
        print("setting value from argu -t tags to :: %s" % args.tags)
        print(tags[0][0])
        tag1 = args.tag[0][0]
        tag_len = len(args.tags[0])
        print(tag_len)
    if args.nums is not None:
        print("numbers: %d", args.nums)
        print(args.nums[0][0])
        num1=args.nums[0][0]
        array_len = len(args.nums[0])
    if args.pushmodel is not None:
        mypushmodel = args.pushmodel
        print("setting value from argu -p pushmodel to :: %s" % mypushmodel)
    ip_addr = args.ip
    username = args.username
    password = args.password

    # Please change this address to camer ip address can be found by using adb shell -> ifconfig
    ip_addr = 'localhost'
    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        # this call we set the camera to dispaly over HDMI
        print(camera_client.configure_preview(resolution="1080P",display_out=1))
        # this call turns on the camera and start transmetting over RTSP and HDMI a stream from camera
        camera_client.set_preview_state("on")
        rtsp_stream_addr = str(camera_client.preview_url)
        print("rtsp stream is :: " + rtsp_stream_addr)
        camera_client.configure_overlay("text", "background images ...")
        camera_client.set_overlay_state("on")
        capture(camera_client, nums=num1, tag='background')
        for i in range(array_len):
            print("array_len: " + str(array_len))
            camera_client.set_overlay_state("off")
            camera_client.configure_overlay("text", tag1 + " images ...")
            camera_client.set_overlay_state("on")
            capture(camera_client, nums=num1, tag=tag1)
        camera_client.set_overlay_state("off")
        camera_client.configure_overlay("text", "Training ...")
        camera_client.set_overlay_state("on")
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
        shutil.rmtree("pictures")
        os.unlink(trainer.CUSTOMVISION_PROJECT_NAME + ".zip")

        # transferring model files to camera for inferencing
        # if mypushmodel.find("True") == -1 :
        if mypushmodel is not True:
            print("Not transferring dlc  as per parameter passed")
        else :
            print("transferring model ,label and va config file as set in create option with -p %s passed" % mypushmodel)
            # utility.transferdlc()
        #Vam(Video analytics engine ) this will take the model and run on thee device 
        camera_client.set_analytics_state("on")
        print(camera_client.vam_url)
        
        # this will set the frames to be overlayed with information recieved from inference results ffrom your model
        camera_client.configure_overlay("inference")

        #Turning overlay to Truse to see inferencing frame overlayed with inference results
        camera_client.set_overlay_state("on")

        # heer we will use gstreamer to get the inference results from camera into thsi module and then send them up to cloud or another module
        try:
            with camera_client.get_inferences() as results:
                print_inferences(results,camera_client,hub_manager)
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

if __name__ == '__main__':
     capture_train()
