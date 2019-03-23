import os
import time
from os import listdir
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient

class Train_Images():
    def __init__(self):
        self.CURRENT_FOLDER = os.getcwd()
        self.IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pictures")
        
        # CUSTOM VISION ACCOUNT SETTINGS
        # Copy keys from https://www.customvision.ai/projects OR https://iris-demo1.azurewebsites.net
        self.TRAINING_KEY = "2402c7d8360f44f081384984f259f468"
        self.TRAINING_ENDPOINT = "https://irisdemo1.azure-api.net/"
        # TRAINING_ENDPOINT = "https://southcentralus.api.cognitive.microsoft.com/"

        # CUSTOM VISION PROJECT SETTINGS
        self.CUSTOMVISION_PROJECT_NAME = "Python Test"
        self.CUSTOMVISION_PROJECT_DOMAIN_ID = "0732100f-1a38-4e49-a514-c9b44c697ab5"
        self.CUSTOMVISION_PROJECT_DESCRIPTION = "Train Test Proj"

    def train_project(self):
        trainer = CustomVisionTrainingClient(self.TRAINING_KEY, endpoint=self.TRAINING_ENDPOINT)

        # Create a new project
        print("Creating project...")
        print(self.CUSTOMVISION_PROJECT_NAME)
        project = trainer.create_project(name=self.CUSTOMVISION_PROJECT_NAME, description=self.CUSTOMVISION_PROJECT_DESCRIPTION, domain_id=self.CUSTOMVISION_PROJECT_DOMAIN_ID)

        # Make tags in based on folder
        tags = [f for f in listdir('pictures')]
        for tag in tags:
            print("Adding images...")
            cur_dir = os.path.join(self.IMAGES_FOLDER, tag)
            tagobj = trainer.create_tag(project.id, tag)
            for image in os.listdir(cur_dir):
                with open(os.path.join(cur_dir, image), mode="rb") as img_data: 
                    trainer.create_images_from_data(project.id, img_data.read(), [ tagobj.id ])

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