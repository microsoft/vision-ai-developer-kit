import argparse
import sys
import time

from camera import CameraClient
# from training_images import Train_Images
import utility

import msvcrt as msv

def capture(camera, nums, tag):
        time.sleep(1)

        print("Start capture images: " + str(nums))
        for x in range(nums):
            if camera.captureImageWithFolder('pictures', tag):
                pass
                #print("capture well and image index:" + str(x))
            else:
                pass
                #print("image capture error and image index:" + str(x))
        print("capture end!")
        time.sleep(10)

def wait(tag):
    #print("AR Camera is going to capture " + str(tag) + "images, please press any key to continue ...")
    #msv.getch()
    pass

def capture_train():
    print("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tags', nargs='+', type=str, dest='tags', action='append', help='please input tag name')
    parser.add_argument('-n', '--nums', nargs='+', type=int, dest='nums', action='append', help='please input numbers of images to capture')
    parser.add_argument('-p','--pushmodel', help ='sets whether to push the model and required files to device or not', default=True)
    parser.add_argument('--ip', help='ip address of the camera', default=utility.getWlanIp())
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    if args.tags is not None:
        tags = [str(tag) for tag in args.tags]
        print("setting value from argu -t tags to :: %s" % args.tags)
        print(tags[0][0])
    tag_len = len(args.tags[0])
    print(tag_len)
    if args.nums is not None:
        nums = [str(n) for n in args.nums]
        print("numbers: %d", args.nums)
        print(nums[0][0])
    array_len = len(args.nums[0])
    if args.pushmodel is not None:
        mypushmodel = args.pushmodel
        print("setting value from argu -p pushmodel to :: %s" % mypushmodel)
    ip_addr = args.ip
    username = args.username
    password = args.password

    # Please change this address to camer ip address can be found by using adb shell -> ifconfig
    # ip_addr = 'localhost'
    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        # camera_client.set_preview_state("off")
        # this call we set the camera to dispaly over HDMI
        print(camera_client.configure_preview(resolution="1080P",display_out=1))
        # this call turns on the camera and start transmetting over RTSP and HDMI a stream from camera
        camera_client.set_preview_state("on")
        rtsp_stream_addr = str(camera_client.preview_url)
        print("rtsp stream is :: " + rtsp_stream_addr)
        camera_client.configure_overlay("text", "background images ...")
        camera_client.set_overlay_state("on")
        #capture(camera_client, nums=args.nums[0][0], tag='background')
        camera_client.set_overlay_state("off")
        for i in range(array_len):
            #print("array_len: " + str(array_len))
            camera_client.configure_overlay("text", str(args.tags[0][i]) + " images ...")
            camera_client.set_overlay_state("on")
            wait(args.tags[0][i])
            capture(camera_client, nums=int(args.nums[0][i]), tag=args.tags[0][i])
            camera_client.set_overlay_state("off")

    # trainer = Train_Images()
    # trainer.train_project()


if __name__ == '__main__':
    capture_train()
