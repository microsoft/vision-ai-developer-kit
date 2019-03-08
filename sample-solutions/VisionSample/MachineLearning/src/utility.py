# ==============================================================================
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.
# ==============================================================================

import time
import os
import subprocess as sp
import sys
import shutil
import socket
import logging
import json
import iot



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.disabled = False
iot_msg_handler = iot.sendip_info_to_portal()

#src = "./var/azureml-app/azureml-models"
#dst = "./var/azureml-app/azureml-models-device"
   
def getWlanIp():
    #if(os.name == "nt") :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        if IP.split('.')[0] == '172':
            print("Ip address detected is :: " + IP )
            IP = '127.0.0.1'
            print("Ip address changed to :: " + IP + "to avoid docker interface")
        print("Ip address detected is :: " + IP )
        
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def prepare_folder(folder):
    print("preparing: %s" % folder)
    if(os.path.isdir(folder)):
        print ("found directory cleaning it before copying new files...")
        #ToDo delete all files in folder 
        shutil.rmtree(folder,ignore_errors=True)
        os.makedirs(folder, exist_ok=True)
    else:
        os.makedirs(folder, exist_ok=True)


def transferdlc(model_name = None):
        
        model_path = getmodelpath(model_name)

        # find root folders
        dirpath = os.getcwd()
        #src = os.path.join(dirpath,"var","azureml-app","azureml-models", model_path)
        src = os.path.join(dirpath,"azureml-models", model_path)
        dst = os.path.abspath("/app/vam_model_folder")

        # find model files
        vamconfig_file = find_file(src, "va-snpe-engine-library_config.json")
        with open(vamconfig_file) as f:
            vamconfig = json.load(f)

        dlc_file = find_file(src, vamconfig["DLC_NAME"])
        label_file = find_file(src, vamconfig["LABELS_NAME"])
        files = [vamconfig_file, dlc_file, label_file]
        print("Found model files: %s in %s" % (files, src))

        # clean up
        prepare_folder(dst)

        # copy across
        for filename in files:
            print("transfering file :: " + filename)
            shutil.copy(os.path.join(filename),dst)

def find_file(input_path, suffix):
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(input_path) for f in filenames if f == suffix]
    if len(files) != 1:
        raise ValueError("Expecting one ending with %s file as input, found %s in %s. Files: %s" % (suffix, len(files), input_path, files))
    return os.path.join(input_path, files[0])

def getmodelpath(model_name):
    with open(os.path.join(sys.path[0],'model_config_map.json')) as file:
        data = json.load(file)
    print(data)

    #toDo Change the hardcoded QCOmDlc below with value read 
    #print(data['models'][0])
    models = data['models']
    if len(models.keys()) == 0:
        raise ValueError("no models found")
    
    if model_name is None:
        # default to the first model
        model_name, model_data = models.popitem()
    else:
        model_data = models[model_name]
    
    # construct the path
    model_id = model_data['id']
    print("using model %s" % model_id)
    mydata = model_id.split(":")
    model_path = os.path.join(*mydata)

    return model_path

# if __name__ == "__main__":
#     transferdlc()



