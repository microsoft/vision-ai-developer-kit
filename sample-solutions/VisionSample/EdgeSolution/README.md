# Develop and deploy an IoT Edge module VisionSampleModule

For users already have DLC files, they can build an IoT Edge module **VisionSampleModule** on a local machine, push it to Azure Container Registry (ACR) repository, and deploy it to a device.

## Setup Build Environment
1. Download and install Docker from [**Get Started with Docker**](https://www.docker.com/get-started).  Don't sign in **Docker Desktop** after Docker installed.

2. Install [**Docker Extension**](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker) to **Visual Studio Code**.

## Build a Local VisionSampleModule Image

1. Rename the default **deployment.template.json** file to **cloud-deployment.template.json** file.
    - **Note:** The default **deployment.template.json** file is used to deploy the container image created by **MachineLearning\scripts\01-convert-model-containerize.py**.

2. Rename **local-deployment.template.json** file to **deployment.template.json** file.

3. Modify **MODULE_NAME**, **REGISTRY_NAME**, **REGISTRY_USER_NAME**, and **REGISTRY_PASSWORD** 4 settings in **.env** file.  Refer to [**Create a container registry**](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry) for more detail.  For example:
    ```<language>
    MODULE_NAME=VisionSampleModule
    REGISTRY_NAME=specificregistryname
    REGISTRY_USER_NAME=specificregistryname
    REGISTRY_PASSWORD=h51ykq+FxrWLszbFDsJuulP/0yH3XQOh
    ```

4. Sign in **Azure Container Registry** by entering the following command in the **Visual Studio Code** integrated terminal:
    ```<language>
    docker login -u <REGISTRY_USER_NAME> -p <REGISTRY_PASSWORD> <REGISTRY_NAME>.azurecr.io  
    ```
5. Copy **DLC** file and its related **labels.txt** and **va-snpe-engine-library_config.json** to **modules\VisionSampleModule\azureml-models** folder.

6. Open **modules\VisionSampleModule\module.json** file and change **version** setting in **tag** property for creating a new version of the module image.

7. Right-clicking on **deployment.template.json** file and select **[Build and Push IoT Edge Solution]** command to generate a new **deployment.json** file in **config** folder, build a module image, and push the image to the specified ACR repository.
    - **Note:** The "**debconf: delaying package configuration, since apt-utils is not installed**" red warning displayed during building process can be ignored.

8. Right-clicking on **config/deployment.json** file, select **[Create Deployment for Single Device]**, and choose the targeted IoT Edge device to deploy the **VisionSampleModule** Image.

**Note:** When your container image is created by **MachineLearning\scripts\01-convert-model-containerize.py**, remember to rename **cloud-deployment.template.json** file back to **deployment.template.json** to generate **deployment.json**.