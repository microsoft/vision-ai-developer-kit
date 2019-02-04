#%% [markdown]
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.

#%% [markdown]
# # Transfer Learning Sample (Local)

#%%
from IPython import get_ipython
import os

# Set directories
current_dir = os.getcwd()
scripts_dir = os.path.join(current_dir, 'MachineLearning/scripts')

retrain_model_dir = os.path.join(current_dir, 'MachineLearning/models/mobilenet-retrain-local')
os.makedirs(retrain_model_dir, exist_ok = True)

# Data directory
data_dir = os.path.join(current_dir, 'MachineLearning/data/soda_cans')

#%%
# Pre-download base model for retrain.py to fix display blocked by sys.stdout.flush()
import os
import tarfile
from urllib.request import urlretrieve

# Download file
def LoadFile(url, dest=None):
    print ('Downloading {} ...\n' .format(url))
    localfile, _  = urlretrieve(url, filename=dest)
    print ('Downloading {} file Done.' .format(localfile))
    return localfile

# Extract files to the current folder
def ExtractFiles(filename):
    if not os.path.exists(filename):
        print('{} not found!' .format(filename))
        return None
    try:
        print ('Extracting files...')
        with tarfile.open(filename) as tar:
            tar.extractall()
    finally:
        print ('Extracting files Done.')
    return None

# Download base model
base_model_dir = '/tmp/imagenet'
base_model_url = 'http://download.tensorflow.org/models/mobilenet_v1_1.0_224_frozen.tgz'
base_model_file = 'mobilenet_v1_1.0_224_frozen.tgz'
os.makedirs(base_model_dir, exist_ok = True)
try:
    os.chdir(base_model_dir)
    if not os.path.exists(base_model_file):
        ExtractFiles(LoadFile(base_model_url, base_model_file))
finally:
    os.chdir(current_dir)

#%% [markdown]
# ### Retrain a new model by soda_cans dataset on a local machine

#%%
# Retrain mobilenet model by run command

get_ipython().run_line_magic('run', '-i MachineLearning/scripts/transfer_learning_scripts/retrain.py \
                                    --image_dir MachineLearning/data/soda_cans \
                                    --architecture mobilenet_1.0_224 \
                                    --output_graph MachineLearning/models/mobilenet-retrain-local/retrained_graph_local.pb \
                                    --output_labels MachineLearning/models/mobilenet-retrain-local/output_labels.txt \
                                    --how_many_training_steps 4000 \
                                    --train_batch_size 100')

#%% [markdown]
# ### Write VAM config file

#%%
# Write a new va-snpe-engine-library_config.json to retrain model directory
import json

content = {
"Engine":0,
"NetworkIO":1,
"ScaleWidth":224,
"ScaleHeight":224,
"PixelNorm":127.5,
"BlueMean":104,
"GreenMean":117,
"RedMean":123,
"TargetFPS":30,
"ConfThreshold":0.0,
"DLC_NAME":"model.dlc",
"LABELS_NAME":"output_labels.txt",
"InputLayers":"input:0",
"OutputLayers":["final_result"],
"ResultLayers":["final_result:0"],
"Runtime":1
}

vam_config_file = os.path.join(retrain_model_dir, 'va-snpe-engine-library_config.json')
with open(vam_config_file, 'w') as vam_file:
    json.dump(content, vam_file, indent=2)

#%% [markdown]
# ### Write model config file

#%%
# Write a new mobilenet_retrain_local_config.py to model_configs directory
retrain_config_file = os.path.join(scripts_dir, 'model_configs/mobilenet_retrain_local_config.py')

template_file = os.path.join(scripts_dir, 'model_configs/config_template.txt')
file = open(template_file)
contents = file.read()
contents = contents.replace('__MODEL_PATH', '"MachineLearning/models/mobilenet-retrain-local/"')
contents = contents.replace('__MODEL_NAME', '"retrained_graph_local.pb"')
contents = contents.replace('__MODEL_TAGS', '{"Device": "peabody", "type": "mobilenet", "area": "iot", "version": "1.0"}')
contents = contents.replace('__MODEL_DESCRIPTION', '"Retrained MobileNet model by soda_cans dataset on a local machine"')
contents = contents.replace('__MODEL_INPUT_NODE', '"input"')
contents = contents.replace('__MODEL_INPUT_DIMS', '"1,224,224,3"')
contents = contents.replace('__MODEL_OUTPUTS_NODES', '["final_result"]')
contents = contents.replace('__IMAGE_NAME', '"mobilenetretrainlocal"')
contents = contents.replace('__IMAGE_TAGS', '["mobilenet"]')
contents = contents.replace('__IMAGE_DESCRIPTION', '"Retrained MobileNet model by soda_cans dataset on a local machine"')
contents = contents.replace('__MODULE_NAME', '"VisionSampleImagenet_retrain_local"')

with open(retrain_config_file, 'wt', encoding='utf-8') as retrain_file:
    retrain_file.write(contents)

#%% [markdown]
# ### Set current model config file

#%%
# Overwrite current_config.py by the new model config file
import shutil

dest_file = os.path.join(scripts_dir, 'model_configs/current_config.py')
shutil.copy(retrain_config_file, dest_file)


