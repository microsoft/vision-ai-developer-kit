import sys
import time
import json
from iotccsdk.camera import CameraClient

SET_STATE_ON = "on"
SET_STATE_OFF = "off"

ip_addr = "10.69.26.44"
username = "admin"
password = "admin"
resolution = "1080P"
overlay_config = "inference"

delay_interval_secs = 5
should_capture_images = False
cap_min_confidence = 50
cap_max_confidence = 70


def main():
    print("\nPython %s\n" % sys.version)

    with CameraClient.connect(ip_address=ip_addr,
                              username=username,
                              password=password) as camera_client:
        try:
            configure_camera(camera_client)
            capture_image(camera_client)
            print_inferences(camera_client)
        except KeyboardInterrupt:
            print("Stopping")
        finally:
            camera_client.set_analytics_state(SET_STATE_OFF)
            camera_client.set_preview_state(SET_STATE_OFF)


def configure_camera(camera_client: CameraClient):
    camera_client.configure_preview(resolution=resolution,
                                    display_out=1)
    camera_client.set_preview_state(SET_STATE_ON)

    # rtsp stream address
    rtsp_stream_addr = str(camera_client.preview_url)
    print("rtsp stream is :: " + rtsp_stream_addr)

    # turn analytics on
    camera_client.set_analytics_state(SET_STATE_ON)
    print(camera_client.vam_url)

    # configure overlay and start it
    camera_client.configure_overlay(overlay_config)
    camera_client.set_overlay_state(SET_STATE_ON)


def print_inferences(camera_client: CameraClient):
    with camera_client.get_inferences() as results:
        last_time = time.time()
        for result in results:
            if time.time() - last_time > delay_interval_secs:
                for inf_obj in result.objects:
                    inference = Inference(inf_obj)
                    if cap_min_confidence < inference.confidence < cap_max_confidence:
                        capture_image(camera_client)
                
                    print(inference.to_json())
                    last_time = time.time()


def capture_image(camera_client: CameraClient):
    if not should_capture_images:
        print("capture image skipped")
        return
    if not camera_client.captureimage():
        print("capture image failed")


class Inference:

    def __init__(self, inference_object):
        self.id = inference_object.id
        # remove junk final character from the label
        self.label = inference_object.label.strip(" .\t\n")
        self.confidence = inference_object.confidence
        self.position_x = inference_object.position.x
        self.position_y = inference_object.position.y
        self.width = inference_object.position.width
        self.height = inference_object.position.height

    def to_json(self):
        return json.dumps(self.__dict__)


if __name__ == '__main__':
    main()
