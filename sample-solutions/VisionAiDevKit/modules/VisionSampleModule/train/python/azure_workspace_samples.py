# Note: The strings are set as sample values
# Project Workspace created once

import __init__
import os, uuid, sys
from azureml.core import Workspace
from azureml.core.model import Model
from azure.storage.blob import BlockBlobService, PublicAccess

# Sample variables
MODEL_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "models")
MODEL_NAME = "plant"
WORKSPACE_NAME = "CVCog-Cui"
MODEL_FILE_NAME = MODEL_FOLDER + "\mydemomodel.TensorFlow.zip"

def workspace_op():

    ws = Workspace.create(name=WORKSPACE_NAME, subscription_id=__init__.azure_subscription_id,
                         resource_group=__init__.azure_resource_group, create_resource_group=False,
                         location=__init__.azure_location)
    # ws = Workspace(subscription_id=__init__.azure_subscription_id, resource_group=__init__.azure_resource_group, workspace_name=WORKSPACE_NAME)
    # ws_obj = ws.get(name=WORKSPACE_NAME, subscription_id=__init__.azure_subscription_id, resource_group=__init__.azure_resource_group)

    print("Model File:", MODEL_FILE_NAME)
    md = Model.register(ws, model_path=MODEL_FILE_NAME, model_name=MODEL_NAME)

    print ("Register Model Done!")

    """from azureml.contrib.iot.model_converters import SnpeConverter

    # submit a compile request
    compile_request = SnpeConverter.convert_caffe_model(ws, source_model=md, mirror_content=True)
    print(compile_request._operation_id)

    compile_request.wait_for_completion(show_output=True)

    converted_model = compile_request.result
    print(converted_model.name, converted_model.url, converted_model.version, converted_model.id, converted_model.created_time)"""

    return md

# Sample variables
container_name ='quickstartblobs'

def azure_blob_op():
    try:
        # Create the BlockBlockService that is used to call the Blob service for the storage account
        block_blob_service = BlockBlobService(account_name=__init__.azure_storage_account_name,
                                              account_key=__init__.azure_storage_account_key)

        # Create a container
        block_blob_service.create_container(container_name)

        # Set the permission so the blobs are public.
        block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

    except Exception as e:
        print(e)
