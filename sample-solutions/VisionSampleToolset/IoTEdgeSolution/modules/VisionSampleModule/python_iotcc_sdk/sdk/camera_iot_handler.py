from abc import ABCMeta, abstractmethod
import json
import time
from utility import get_file,send_system_cmd,getWlanIp
import iot
from camera import CameraClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_url = ""
label_url = ""
config_url = ""
restartCamera = False
msg_per_minute = 5
wait_for_minutes = 12
object_of_interest = "ALL"
start_time = 0
class IotHandler(metaclass = ABCMeta):
    @abstractmethod
    def module_twin_callback(self):
        pass
class CameraIoTHandler(IotHandler):
    def __init__(self,camera_cleint):
        self.mycamera_cleint = camera_cleint
        #getting Iot hub sdk ready with hub manager
        self.hub_manager = iot.HubManager(self)

    def send_rtsp_info(self):
        #uploading rtsp stream address to iot hub as twin property so that user one can know what there rtsp address is and then use it on vlc media player 
        self.hub_manager.iothub_client_sample_run(str(self.mycamera_cleint.preview_url))
    def print_and_send_results(self):
            with self.mycamera_cleint.get_inferences() as results:
                self.print_inferences(results,self.hub_manager)
                #self.send_message_to_cloud(result,self.hub_manager)
                print("Restarting get inference and print again!!!")
        
    def print_inferences(self,results=None,hub_manager=None):
        global wait_for_minutes
        global start_time
        try:
            logging.debug("")
            start_time = time.time()
            for result in results:
                if result is not None and result.objects is not None and len(result.objects):
                    timestamp = result.timestamp
                    if timestamp:
                        logging.debug("timestamp={}".format(timestamp))
                    else:
                        logging.debug("timestamp= " + "None")
                    for object in result.objects:
                        id = object.id
                        label = object.label
                        confidence = object.confidence
                        x = object.position.x
                        y = object.position.y
                        w = object.position.width
                        h = object.position.height
                        logging.debug("id={}".format(id))
                        logging.debug("label={}".format(label))
                        logging.debug("confidence={}".format(confidence))
                        location = "Position(x,y,w,h)=" + str(x) + "," + str(y) + "," + str(w) + "," + str(h)
                        logging.debug(location)
                        result = {"label":label,
                                    "confidence":confidence}
                                    #"location" : location}
                        #self.send_message_to_cloud
                        dataToCloud= json.dumps(result)
                        #Checking if time to send message to make sure we are not sending more messages then set in twin
                        if(time.time() - start_time > wait_for_minutes):
                            #Checking if Object Of Interest returned from tarined mdoel is found to send alert to cloud

                            if(object_of_interest=="ALL" or object_of_interest.lower() in label.lower()):
                                logging.debug("I see " + str(label) + " with confidence :: " + str(confidence))
                                hub_manager.SendMsgToCloud(dataToCloud)
                                start_time = time.time()
                            else:
                                logging.debug("Not sending to cloud as notification is set for only label::" + object_of_interest)
                        else:
                            logging.debug("skipping sending msg to cloud until :: " + str(wait_for_minutes - ((time.time() - start_time))))
                        logging.debug("")
                else:
                    logging.info("No results")
                        #restartInference()
                    #return
        except Exception as e:
            logging.info("got issue during print")
            logging.exception(e)
            raise

    def send_message_to_cloud(self,result,hub_manager):

        global start_time
        dataToCloud= json.dumps(result)
        #Checking if time to send message to make sure we are not sending more messages then set in twin 
        if(time.time() - start_time > wait_for_minutes):
            #Checking if Object Of Interest returned from tarined mdoel is found to send alert to cloud
            if(object_of_interest=="ALL" or object_of_interest.lower() in result.label.lower()):
                logging.debug("I see " + str(result.label) + " with confidence :: " + str(result.confidence))
                hub_manager.SendMsgToCloud(dataToCloud)
                start_time = time.time()
            else:
                logging.debug("Not sending to cloud as notification is set for only label::" + object_of_interest)
        else:
            logging.debug("skipping sending msg to cloud until :: " + str(wait_for_minutes - ((time.time() - start_time))))
        logging.debug("")

    def module_twin_callback(self,update_state, payload, user_context):
        global model_url
        global label_url
        global config_url
        global msg_per_minute
        global wait_for_minutes
        global object_of_interest 
        print ( "" )
        print ( "Twin callback called with:" )
        print ( "    updateStatus: %s" % update_state )
        print ( "    payload: %s" % payload )
        data = json.loads(payload)
        setRestartCamera = False

        if "desired" in data and "model_url" in data["desired"]:
            model_url = data["desired"]["model_url"]
            if model_url:
                print("Setting value to %s from ::  data[\"desired\"][\"model_url\"]" % model_url)
                setRestartCamera = get_file(model_url)
            else:
                print(model_url)
        if "model_url" in data:
            model_url = data["model_url"]
            if model_url:
                print("Setting value to %s from ::  data[\"model_url\"]" % model_url)
                setRestartCamera = get_file(model_url)

        if "desired" in data and "label_url" in data["desired"]:
            label_url = data["desired"]["label_url"]
            if label_url:
                print("Setting value to %s from ::  data[\"desired\"][\"label_url\"]" % label_url)
                setRestartCamera = get_file(label_url)
            else:
                print(label_url)
        if "label_url" in data:
            label_url = data["label_url"]
            if label_url:
                print("Setting value to %s from ::  data[\"label_url\"]" % label_url)
                setRestartCamera = get_file(label_url)

        if "desired" in data and "config_url" in data["desired"]:
            config_url = data["desired"]["config_url"]
            if config_url:
                print("Setting value to %s from ::  data[\"desired\"][\"config_url\"]" % config_url)
                setRestartCamera = get_file(config_url)

        if "config_url" in data:
            config_url = data["config_url"]
            if config_url:
                print("Setting value to %s from ::  data[\"config_url\"]" % config_url)
                setRestartCamera = get_file(config_url)

        if "desired" in data and "msg_per_minute" in data["desired"]:
            
            msg_per_minute = data["desired"]["msg_per_minute"]
            msg_per_minute = 60/int(msg_per_minute)
            print("Setting value to %s from ::  data[\"msg_per_minute\"]" % msg_per_minute)

        if "msg_per_minute" in data:
            msg_per_minute = data["msg_per_minute"]
            wait_for_minutes = int(60/int(msg_per_minute))

            print("Setting value to %s from ::  data[\"msg_per_minute\"]" % msg_per_minute)

        if "desired" in data and "object_of_interest" in data["desired"]:
            object_of_interest = data["desired"]["object_of_interest"]
            print("Setting value to %s from ::  data[\"object_of_interest\"]" % object_of_interest)

        if "object_of_interest" in data:
            msg_per_minute = data["object_of_interest"]
            print("Setting value to %s from ::  data[\"object_of_interest\"]" % object_of_interest)
        if setRestartCamera:
            #
            try:
                logging.info("Restarting VAM to apply new model config")
                self.restartInference(self.mycamera_cleint)
                
            except Exception as e:
                logging.info("Got an issue during vam ON off after twin update")
                logging.exception(e)
                raise
    def restartInference(self,camera_client) :

        try:

            logging.debug("Restarting VAM to apply new model config")
            camera_client.set_overlay_state("off")
            if(camera_client.vam_running):
                camera_client.set_analytics_state("off")
            time.sleep(1)
            camera_client.set_analytics_state("on")
            camera_client.set_overlay_state("on")
            self.print_and_send_results()

        except Exception as e:
            logging.debug("we have got issue during vam ON off after camer switch ")
            logger.exception(e)
            #self.restart_cam(camera_client)
            raise

            #TO DO 
            # Try recovery here 
    
    def restart_cam(self,camera_client = None):

        try:
            # turning everything off and logging out ...
            camera_client.logout()
            if camera_client is not None:
                camera_client = None
            send_system_cmd("systemctl restart qmmf-webserver")
            time.sleep(1)
            send_system_cmd("systemctl restart ipc-webserver")
            time.sleep(1)
            raise Exception
        except Exception as e:
            logging.debug("we have got issue during Logout and Login restarting camera now...")
            send_system_cmd("systemctl reboot")
            logger.exception(e)
            raise
            #this call we set the camera to dispaly over HDMI 
