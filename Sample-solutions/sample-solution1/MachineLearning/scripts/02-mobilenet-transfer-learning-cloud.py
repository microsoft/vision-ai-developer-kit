#%% [markdown]
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.

#%% [markdown]
# # Transfer Learning Sample (Cloud)


#%%
# Check core SDK version number
import azureml.core

print('SDK version: {}' .format(azureml.core.VERSION))

#%%
# The current working directory is workspace root.
import os

# Set directories
current_dir = os.getcwd()
scripts_dir = os.path.join(current_dir, 'MachineLearning/scripts')
data_dir = os.path.join(current_dir, 'MachineLearning/data/soda_cans')

retrain_scripts_dir = os.path.join(scripts_dir, 'transfer_learning_scripts')
retrain_model_dir = os.path.join(current_dir, 'MachineLearning/models/mobilenet-retrain-cloud')
os.makedirs(retrain_model_dir, exist_ok = True)

#%% [markdown]
# ### Connect a Workspace


#%%
#Initialize Workspace 
from azureml.core import Workspace

ws = Workspace.from_config()
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep = '\n')

#%% [markdown]
# ### Create Experiment
# Experiment is a logical container in an Azure ML Workspace. It hosts run records which can include run metrics and output artifacts from your experiments.

#%%
experiment_name = 'soda_cans'

from azureml.core import Experiment
exp = Experiment(workspace = ws, name = experiment_name)

#%% [markdown]
# ### Upload data files into datastore
# Every workspace comes with a default datastore (and you can register more) which is backed by the Azure blob storage account associated with the workspace. We can use it to transfer data from local to the cloud, and access it from the compute target.

#%%
# get the default datastore
ds = ws.get_default_datastore()
print(ds.name, ds.datastore_type, ds.account_name, ds.container_name)


#%%
data_target_path = experiment_name + '_training_data'
ds.upload(src_dir=data_dir, target_path=data_target_path, overwrite=True)

#%% [markdown]
# ### Configure for using ACI
# Linux-based ACI is available in West US, East US, West Europe, North Europe, West US 2, Southeast Asia, Australia East, East US 2, and Central US regions.  See details [here](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-quotas#region-availability)

#%%
from azureml.core.runconfig import DataReferenceConfiguration
dr = DataReferenceConfiguration(datastore_name=ds.name, 
                   path_on_datastore=data_target_path, 
                   mode='download', # download files from datastore to compute target
                   overwrite=True)

#%% [markdown]
# Set the system to build a conda environment based on the run configuration. Once the environment is built, and if you don't change your dependencies, it will be reused in subsequent runs.

#%%
from azureml.core.compute import AmlCompute
from azureml.core.compute import ComputeTarget

# choose a name for your cluster
compute_name = "cpucluster"
compute_min_nodes = 0
compute_max_nodes = 2

# This example uses CPU VM. For using GPU VM, set SKU to STANDARD_NC6
vm_size = "Standard_D3"

if compute_name in ws.compute_targets:
    compute_target = ws.compute_targets[compute_name]
    if compute_target and type(compute_target) is AmlCompute:
        print('found compute target. just use it. ' + compute_name)
else:
    print('creating a new compute target...')
    provisioning_config = AmlCompute.provisioning_configuration(vm_size = vm_size,
                                                                min_nodes = compute_min_nodes, 
                                                                max_nodes = compute_max_nodes)

    # create the cluster
    compute_target = ComputeTarget.create(ws, compute_name, provisioning_config)

    # can poll for a minimum number of nodes and for a specific timeout. 
    # if no min node count is provided it will use the scale settings for the cluster
    compute_target.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)

     # For a more detailed view of current AmlCompute status, use the 'status' property    
    print(compute_target.status.serialize())

#%%
from azureml.core.runconfig import RunConfiguration

# create a new runconfig object
run_config = RunConfiguration.load('.', 'aci')
run_config.target = compute_target.name

# set the data reference of the run configuration
run_config.data_references = {ds.name: dr}

#%% [markdown]
# ### Submit the Experiment
# Submit script to run in the Docker image in the remote VM. If you run this for the first time, the system will download the base image, layer in packages specified in the conda_dependencies.yml file on top of the base image, create a container and then execute the script in the container.

#%%
from azureml.core import Run
from azureml.core import ScriptRunConfig

src = ScriptRunConfig(source_directory = retrain_scripts_dir, script = 'retrain.py', run_config = run_config, 
                      # pass the datastore reference as a parameter to the training script
                      arguments=['--image_dir', str(ds.as_download()),
                                 '--architecture', 'mobilenet_1.0_224',
                                 '--output_graph', 'outputs/retrained_graph.pb',
                                 '--output_labels', 'outputs/output_labels.txt'
                                ])
run = exp.submit(config=src)


#%%
run


#%%
run.wait_for_completion(show_output=True)

#%% [markdown]
# ### Register the model


#%%
from azureml.core.model import Model

# This is registering the model from the run object.  It's different than the other sample notebook that uses the local
# file from the Model objec.
model = run.register_model(model_name = experiment_name,
                           model_path = 'outputs/')

print(model.name, model.url, model.version, model.id, model.created_time)

#%% [markdown]
# ### Download the model

#%%
model.download(target_dir = retrain_model_dir)

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

vam_config_file = os.path.join(retrain_model_dir, 'outputs/va-snpe-engine-library_config.json')
with open(vam_config_file, 'w') as vam_file:
    json.dump(content, vam_file, indent=2)

#%% [markdown]
# ### Write model config file


#%%
# Write a new mobilenet_retrain_cloud_config.py to model_configs directory
retrain_config_file = os.path.join(scripts_dir, 'model_configs/mobilenet_retrain_cloud_config.py')

template_file = os.path.join(scripts_dir, 'model_configs/config_template.txt')
file = open(template_file)
contents = file.read()
contents = contents.replace('__MODEL_PATH', '"MachineLearning/models/mobilenet-retrain-cloud/outputs/"')
contents = contents.replace('__MODEL_NAME', '"retrained_graph.pb"')
contents = contents.replace('__MODEL_TAGS', '{"Device": "peabody", "type": "mobilenet", "area": "iot", "version": "1.0"}')
contents = contents.replace('__MODEL_DESCRIPTION', '"Retrained MobileNet model by soda_cans dataset"')
contents = contents.replace('__MODEL_INPUT_NODE', '"input"')
contents = contents.replace('__MODEL_INPUT_DIMS', '"1,224,224,3"')
contents = contents.replace('__MODEL_OUTPUTS_NODES', '["final_result"]')
contents = contents.replace('__IMAGE_NAME', '"mobilenetretraincloud"')
contents = contents.replace('__IMAGE_TAGS', '["mobilenet"]')
contents = contents.replace('__IMAGE_DESCRIPTION', '"Retrained MobileNet model by soda_cans dataset"')
contents = contents.replace('__MODULE_NAME', '"VisionSampleImagenet_retrain_cloud"')

with open(retrain_config_file, 'wt', encoding='utf-8') as retrain_file:
    retrain_file.write(contents)

#%% [markdown]
# ### Set current model config file

#%%
# Overwrite current_config.py by the new model config file
import shutil

dest_file = os.path.join(scripts_dir, 'model_configs/current_config.py')
shutil.copy(retrain_config_file, dest_file)