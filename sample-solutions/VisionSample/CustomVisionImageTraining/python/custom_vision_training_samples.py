import os, __init__
import time

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient

MODEL_NAME = "plant"
WORKSPACE_NAME = "CVCog-Cui"
CURRENT_FOLDER = os.getcwd()
IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "images")
MODEL_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "IoTEdgeSolution", "modules", "VisionSampleModule", "model")

def train_project(subscription_key):

    trainer = CustomVisionTrainingClient(subscription_key, endpoint=__init__.TRAINING_ENDPOINT)

    # Create a new project
    print("Creating project...")
    print(__init__.CUSTOMVISION_PROJECT_NAME)
    project = trainer.create_project(name=__init__.CUSTOMVISION_PROJECT_NAME, description=__init__.CUSTOMVISION_PROJECT_DESCRIPTION, domain_id=__init__.CUSTOMVISION_PROJECT_DOMAIN_ID)
    # domains = trainer.get_domains()
    # for domain in domains:
    #     print(domain)
    # project = trainer.create_project(name=__init__.CUSTOMVISION_PROJECT_NAME)
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
    performance = trainer.get_iteration_performance(project.id, iteration.id)
    print("Performance Precision: " + str(performance.precision))
    print("Precision STD Deviation: " + str(performance.precision_std_deviation))
    exports = trainer.get_exports(project.id, iteration.id)
    for export_type in exports:
        print(export_type)
    print("Training Done!")
    print("Please downlaod your model from customvisison.ai portal until we GA this build this step need to be done manually ...")

    return project

if __name__ == "__main__":
    my_project = train_project(__init__.TRAINING_KEY)
    # trainer = CustomVisionTrainingClient(__init__.TRAINING_KEY, endpoint=__init__.TRAINING_ENDPOINT)
    # trainer.delete_project(my_project.id)
