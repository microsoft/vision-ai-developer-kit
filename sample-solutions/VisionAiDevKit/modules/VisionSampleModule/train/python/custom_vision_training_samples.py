import os, __init__
import time

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient

from azureml.core import Workspace
from azureml.core.model import Model

MODEL_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "models")
MODEL_NAME = "plant"
WORKSPACE_NAME = "CVCog-Cui"
FILE_MODEL_DLC = MODEL_FOLDER + "model.dlc"
FILE_LABEL_TXT = MODEL_FOLDER + "labels.txt"
FILE_PROTO_TXT = MODEL_FOLDER + "model.prototxt"
FILE_ZIPPED = MODEL_FOLDER + "3dc35062e84d43dcb39c6d98cdd358df.VAIDK.zip"
IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "images")
MODELS_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "models")

def train_project(subscription_key):

    trainer = CustomVisionTrainingClient(subscription_key, endpoint=__init__.ENDPOINT)

    # Create a new project
    print("Creating project...")
    print(__init__.SAMPLE_PROJECT_NAME)
    project = trainer.create_project(name=__init__.SAMPLE_PROJECT_NAME, domain_id="0732100f-1a38-4e49-a514-c9b44c697ab5")
    # project = trainer.create_project(name=__init__.SAMPLE_PROJECT_NAME)
    # Make two tags in the new project
    hemlock_tag = trainer.create_tag(project.id, "Hemlock")
    cherry_tag = trainer.create_tag(project.id, "Japanese Cherry")

    print("Adding images...")
    hemlock_dir = os.path.join(IMAGES_FOLDER, "Hemlock")
    for image in os.listdir(hemlock_dir):
        with open(os.path.join(hemlock_dir, image), mode="rb") as img_data: 
            trainer.create_images_from_data(project.id, img_data.read(), [ hemlock_tag.id ])
    
    cherry_dir = os.path.join(IMAGES_FOLDER, "Japanese Cherry")
    for image in os.listdir(cherry_dir):
        with open(os.path.join(cherry_dir, image), mode="rb") as img_data: 
            trainer.create_images_from_data(project.id, img_data.read(), [ cherry_tag.id ])

    print ("Training...")
    iteration = trainer.train_project(project.id)
    while (iteration.status == "Training"):
        iteration = trainer.get_iteration(project.id, iteration.id)
        print ("Training status: " + iteration.status)
        time.sleep(1)

    # The iteration is now trained. Make it the default project endpoint
    trainer.update_iteration(project.id, iteration.id, is_default=True)
    print("Training Done!")
    print("Please downlaod your model from customvisison.ai portal until we GA this build this step need to be done manually ...")

    """ print("Export model ...")
    export_raw_data = trainer.export_iteration(project.id, iteration.id, platform='TensorFlow', raw=False)
    model_file = __init__.SAMPLE_PROJECT_NAME + '.raw'
    with open(os.path.join(MODELS_FOLDER, model_file), 'wb') as datafile:
        datafile.write(export_raw_data)
    model_file.close()
    print("Exported ...", model_file)
    return model_file """


    return project

def workspace_create():
    ws = Workspace.create(name=WORKSPACE_NAME, subscription_id=__init__.azure_subscription_id,
                         resource_group=__init__.azure_resource_group, create_resource_group=True,
                         location=__init__.azure_location)
    print("Workspace created ...")
    return ws

def workspace_retrieve():
    ws = Workspace(subscription_id=__init__.azure_subscription_id, resource_group=__init__.azure_resource_group, workspace_name=WORKSPACE_NAME)
    print(WORKSPACE_NAME + "Existing workspace retrieved")
    return ws

def model_register_convert(ws):
    print("Model File:", MODEL_NAME)

    # md = Model.register(ws, model_path=MODEL_FILE_NAME, model_name=MODEL_NAME)
    md = Model.register(ws, model_path = FILE_ZIPPED,
                        model_name = MODEL_NAME,
                        description = "Not sure about the description")
    print("Register Model Done!")

    from azureml.contrib.iot.model_converters import SnpeConverter

    # submit a compile request
    compile_request = SnpeConverter.convert_caffe_model(ws, source_model=md, mirror_content=True)
    print(compile_request._operation_id)

    compile_request.wait_for_completion(show_output=True)

    converted_model = compile_request.result
    print(converted_model.name, converted_model.url, converted_model.version, converted_model.id, converted_model.created_time)

def register_model(ws):
    print("Model File:", MODEL_NAME)
    md = Model.register(ws, model_path=FILE_ZIPPED, model_name=MODEL_NAME)

    print ("Register Model Done!")
if __name__ == "__main__":
    #my_project = train_project(__init__.SUBSCRIPTION_KEY_ENV_NAME)

    # trainer = CustomVisionTrainingClient(__init__.SUBSCRIPTION_KEY_ENV_NAME, endpoint=__init__.ENDPOINT)
    # trainer.delete_project(my_project.id)
    # from tools import execute_samples
    # execute_samples(globals(), SUBSCRIPTION_KEY_ENV_NAME)
    # workspace = workspace_create()
    workspace = workspace_retrieve()
    register_model(workspace)
