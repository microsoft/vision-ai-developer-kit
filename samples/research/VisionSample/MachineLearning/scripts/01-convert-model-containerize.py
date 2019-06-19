#%% [markdown]
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.
#%% [markdown]
# # Convert Model and Containerize
# * Connect Workspace
# * Register Model
# * Convert Model
# * Build Container Image
# * Write .ENV File

#%%
# Check core SDK version number
import azureml.core

print('SDK version: {}' .format(azureml.core.VERSION))

#%%
# The current working directory is workspace root.
import os

def ChangeDir(new_dir):
    try:
        os.chdir(new_dir)
    except:
        return False
    return True

# Set current, scripts, src directories
current_dir = os.getcwd()
print('The current directory is {}.' .format(current_dir))

scripts_dir = os.path.join(current_dir, 'MachineLearning\\scripts')
src_dir = os.path.join(current_dir, 'MachineLearning\\src')

# Import model settings from current_config.py
if ChangeDir(scripts_dir):
    from model_configs.current_config import cfg
    print('Model Path: {}' .format(cfg.MODEL_PATH))
    ChangeDir(current_dir)
else:
    raise Exception('Fail to import current_config.py file \
caused by cannot change directory to {}.\n\
Please check whether the current directory opened by \
[Open Folder] command is VisionSample directory or not.  \
Refer to README.md for more detail.' .format(scripts_dir))


#%% [markdown]
# ## Connect Workspace
# 

#%%
#Initialize Workspace 
from azureml.core import Workspace
ws = Workspace.from_config()

print('workspace information:')
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep = '\n')

#%% [markdown]
# ## Register Model

#%%
from azureml.core.model import Model

model = Model.register(model_path = cfg.MODEL_PATH,
                       model_name = cfg.MODEL_NAME,
                       tags = cfg.MODEL_TAGS,
                       description = cfg.MODEL_DESCRIPTION,
                       workspace = ws)

print('model information:')
print(model.name, model.url, model.version, model.id, model.created_time)

#%% [markdown]
# ## Convert Model

#%%
from azureml.contrib.iot.model_converters import SnpeConverter

print(cfg.SNPECONVERTER_TYPE.lower())
if cfg.SNPECONVERTER_TYPE.lower() == "tensorflow":
    # submit a compile request
    compile_request = SnpeConverter.convert_tf_model(
        ws,
        source_model = model,
        input_node = cfg.MODEL_INPUT_NODE,
        input_dims = cfg.MODEL_INPUT_DIMS,
        outputs_nodes = cfg.MODEL_OUTPUTS_NODES,
        allow_unconsumed_nodes = True)
elif cfg.SNPECONVERTER_TYPE.lower() == "caffe":
    # submit a compile request
    compile_request = SnpeConverter.convert_caffe_model(
        ws,
        source_model=model,
        mirror_content = True)

try:
    print('compile_request information:')
    print(compile_request._operation_id)
except:
    print("Fail to convert. Please check __BASE.SNPECONVERTER_TYPE in current_config.py")

#%%
try:
    # Wait for the request to complete
    print('Wait for the request to complete...')
    compile_request.wait_for_completion(show_output=True, timeout=None)
except:
    print("Fail to convert. Please check __BASE.SNPECONVERTER_TYPE in current_config.py")


#%%
# Get the converted model
converted_model = compile_request.result

print('converted_model information:')
print(converted_model.name, converted_model.url, converted_model.version, converted_model.id, converted_model.created_time)

#%% [markdown]
# ## Build Container Image

#%%
from azureml.core.image import Image
from azureml.contrib.iot import IotContainerImage

print ('Start to create a container image ...')

# Change working directory to the main.py location
ChangeDir(src_dir)
print('src directory: {}' .format(os.getcwd() ))

image_config = IotContainerImage.image_configuration(
                                 architecture="arm32v7",
                                 execution_script="main.py", 
                                 dependencies=["camera.py","iot.py","ipcprovider.py","utility.py", "frame_iterators.py"],
                                 docker_file="Dockerfile", 
                                 tags = cfg.IMAGE_TAGS,
                                 description = cfg.IMAGE_DESCRIPTION)

image = Image.create(name = cfg.IMAGE_NAME,
                     # this is the model object 
                     models = [converted_model],
                     image_config = image_config, 
                     workspace = ws)

image.wait_for_creation(show_output = True)

# Change working directory back to workspace root.
ChangeDir(current_dir)
print('current directory: {}' .format(os.getcwd() ))

#%% [markdown]
# ## Write .ENV File

#%%
# Getting your container details
container_reg = ws.get_details()["containerRegistry"]
reg_name = container_reg.split("/")[-1]
container_url = "\"" + image.image_location + "\","
subscription_id = ws.subscription_id
resource_group_name = ws.resource_group

print('Image location: {}'.format(image.image_location))
print('Register name: {}'.format(reg_name))
print('Subscription: {}'.format(subscription_id))
print('Resource group: {}'.format(resource_group_name))

from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt import containerregistry

client = ContainerRegistryManagementClient(ws._auth,subscription_id)
result = client.registries.list_credentials(resource_group_name, reg_name, custom_headers=None, raw=False)
username = result.username
password = result.passwords[0].value

#%%
with open('DeployContainerFromAML/.env', 'w') as env_file:
    env_file.write("MODULE_NAME={}\n" .format(cfg.MODULE_NAME))
    env_file.write("REGISTRY_NAME={}\n" .format(reg_name))
    env_file.write("REGISTRY_USER_NAME={}\n" .format(username))
    env_file.write("REGISTRY_PASSWORD={}\n" .format(password))
    env_file.write("REGISTRY_IMAGE_LOCATION={}\n" .format(image.image_location))