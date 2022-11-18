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
data_dir = os.path.join(current_dir, 'MachineLearning/data/poker6')

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
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar)
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
# ### Retrain a new MobileNet V1 model with poker6 dataset on a local machine

#%%
# Retrain mobilenet model by run command

get_ipython().run_line_magic('run', '-i MachineLearning/scripts/transfer_learning_scripts/retrain.py \
                                    --image_dir MachineLearning/data/poker6 \
                                    --architecture mobilenet_1.0_224 \
                                    --output_graph MachineLearning/models/mobilenet-retrain-local/retrained_graph_local.pb \
                                    --output_labels MachineLearning/models/mobilenet-retrain-local/output_labels.txt \
                                    --how_many_training_steps 1000 \
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
# ### Set current model config file

#%%
# Overwrite current_config.py by the new model config file
import shutil

retrain_config_file = os.path.join(scripts_dir, 'model_configs/mobilenet_retrain_local_config.py')
dest_file = os.path.join(scripts_dir, 'model_configs/current_config.py')
shutil.copy(retrain_config_file, dest_file)


