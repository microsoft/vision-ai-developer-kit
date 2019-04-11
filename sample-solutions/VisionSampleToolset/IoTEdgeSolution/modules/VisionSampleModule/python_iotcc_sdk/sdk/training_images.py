# ==============================================================================
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.
# ==============================================================================

import os
import time
import urllib.request
from os import listdir
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient

class Train_Images():
    def __init__(self):
        self.CURRENT_FOLDER = os.getcwd()
        self.IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__name__)), "pictures")
        # self.IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pictures")
        # CUSTOM VISION ACCOUNT SETTINGS
        # Copy keys from https://www.customvision.ai/projects OR https://iris-demo1.azurewebsites.net
        # self.TRAINING_KEY = ""
        self.TRAINING_KEY = "training key"
        self.TRAINING_ENDPOINT = "https://southcentralus.api.cognitive.microsoft.com/"

        # CUSTOM VISION PROJECT SETTINGS
        self.CUSTOMVISION_PROJECT_NAME = "SelfCapture"
        self.CUSTOMVISION_PROJECT_DOMAIN_ID = "0732100F-1A38-4E49-A514-C9B44C697AB5"
        self.CUSTOMVISION_PROJECT_DESCRIPTION = "Train Images that AR camera captures"

    def train_project(self):
        trainer = CustomVisionTrainingClient(self.TRAINING_KEY, endpoint=self.TRAINING_ENDPOINT)
        platform = ["VAIDK", "TensorFlow", "DockerFile", "CoreML"]
        # Create a new project
        print("Creating project...")
        print(self.CUSTOMVISION_PROJECT_NAME + platform[0])
        project = trainer.create_project(self.CUSTOMVISION_PROJECT_NAME,
            description=self.CUSTOMVISION_PROJECT_DESCRIPTION,
            domain_id=self.CUSTOMVISION_PROJECT_DOMAIN_ID,
            classification_type='Multiclass',
            target_export_platforms=platform)

        # Make tags in based on folder
        tags = [f for f in listdir('pictures')]
        for tag in tags:
            print("Adding images...")
            cur_dir = os.path.join(self.IMAGES_FOLDER, tag)
            tagobj = trainer.create_tag(project.id, tag)
            for image in os.listdir(cur_dir):
                with open(os.path.join(cur_dir, image), mode="rb") as img_data:
                    trainer.create_images_from_data(project.id, img_data.read(), [ tagobj.id ])

        print("Training...")
        iteration = trainer.train_project(project.id)
        # iteration = trainer.get_iteration(project.id, '24940d46-941f-433f-92b7-a802a62e8743')
        while (iteration.status == "Training"):
            iteration = trainer.get_iteration(project.id, iteration.id)
            print("Training status: " + iteration.status)
            time.sleep(1)

        # The iteration is now trained. Make it the default project endpoint
        trainer.update_iteration(project.id, iteration.id, name=iteration.id)
        performance = trainer.get_iteration_performance(project.id, iteration.id)
        print("Performance Precision: " + str(performance.precision))
        print("Precision STD Deviation: " + str(performance.precision_std_deviation))
        export = trainer.export_iteration(project.id, iteration.id, "VAIDK")
        print("export: " + str(export) + "\n" +
              "project id: " + project.id + "\n" +
              "iteration id: " + iteration.id)

        exported_iterations = trainer.get_exports(project.id, iteration.id)
        while exported_iterations[0].status != "Done":
            time.sleep(1)
            exported_iterations = trainer.get_exports(project.id, iteration.id)

        print(exported_iterations[0].status, exported_iterations[0].platform, exported_iterations[0].download_uri)
        urllib.request.urlretrieve(exported_iterations[0].download_uri, self.CUSTOMVISION_PROJECT_NAME+".zip")
        print("Training Done!" + self.CUSTOMVISION_PROJECT_NAME + ".zip downloaded at current folder.")

        return project

# if __name__ == '__main__':
#     trainer = Train_Images()
#     trainer.train_project()
