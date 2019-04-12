# Develop and deploy an IoT Edge module VisionSampleModule

For users already have DLC files, they can build an IoT Edge module **VisionSampleModule** on a local machine, push it to Azure Container Registry (ACR) repository, and deploy it to a device.

## Setup Build Environment
1. Download and install Docker from [**Get Started with Docker**](https://www.docker.com/get-started).  Don't sign in **Docker Desktop** after Docker installed.

2. Install [**Docker Extension**](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker) to **Visual Studio Code**.

## Build a Local Container Image with a Single Module: VisionSampleModule

modules\\**VisionSampleModule** folder includes:
   * **app** folder: source code used to detect objects by a deep learning model.
   * **model** folder: a deep learning model's dlc file, its related labels.txt file and va-snpe-engine-library_config.json.  The default model.dlc is a classfication model trained by Azure Custom Vision Service to detect "fork" and "scissors" two classes.
   * **Dockerfile.arm32v7** file: instructions used to build this module image.
   * **module.json** file: config file for this module.

1. Overwrite **deployment.template.json**'s content by **01-visionsample-deployment.template.json** file.  It only includes one modeule: VisionSampleModule.

2.  Update the **.env** file with the values for your container image name and container registry.  Refer to [**Create a container registry**](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry) for more detail about ACR settings.
     ```<language>
     MODULE_NAME="Your container image name"
     REGISTRY_NAME="Your ACR name"
     REGISTRY_USER_NAME="Your ACR username"
     REGISTRY_PASSWORD="Your ACR password"
     ```

3. Sign in **Azure Container Registry** by entering the following command in the **Visual Studio Code** integrated terminal (replace <REGISTRY_USER_NAME>, <REGISTRY_PASSWORD>, and <REGISTRY_NAME> to your container registry values set in the **.env** file):
    ```<language>
    docker login -u <REGISTRY_USER_NAME> -p <REGISTRY_PASSWORD> <REGISTRY_NAME>.azurecr.io  
    ```
4. Copy **DLC** file and its related **labels.txt** and **va-snpe-engine-library_config.json** to **modules\VisionSampleModule\model** folder.

5. Open **modules\VisionSampleModule\module.json** file and change **version** setting in **tag** property for creating a new version of the module image.

6. Right-clicking on **deployment.template.json** file and select **[Build and Push IoT Edge Solution]** command to generate a new **deployment.json** file in **config** folder, build a module image, and push the image to the specified ACR repository.
    > **Note:** Some red warnings "**/usr/bin/find: '/proc/XXX': No such file or directory**" and "**debconf: delaying package configuration, since apt-utils is not installed**" displayed during the building process can be ignored.

7. Right-clicking on **config/deployment.json** file, select **[Create Deployment for Single Device]**, and choose the targeted IoT Edge device to deploy the container Image.

## Build a Local Image with Two Modules: VisionSampleModule and BusinessLogicModule 

modules\\**BusinessLogicModule** folder includes:
   * **Dockerfile.arm32v7** file: instructions used to build this module image.
   * **main.py** file: implements a business logic to send a detected message received from VisionSampleModule with adding an extra property ["MessageSender", "BusinessLogicModule"] to IoT Hub while detecting a target object, for example: “scissors”.  
Refer to [Tutorial: Deploy Azure functions as IoT Edge modules](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-deploy-function) for more detail about business logic.
   * **module.json** file: config file for this module.
   *  **requirements.txt** file: Python packages required to be installed .

1. Overwrite **deployment.template.json**'s content by **02-visionsample-deployment.template.json** file.  It includes two modules: VisionSampleModule and BusinessLogicModule.
Base on the model copied to the **modules\VisionSampleModule\model** folder to change the setting **ObjectOfInterest** at the end of deployment.template.json file to the object label you want to send a detected messgae to Azure IoT Hub.

2. Use the same build steps listed in [Build a Local Container Image with a Single Module: VisionSampleModule] section to build a local container image with two modules.

3. Select [AZURE IOT HUB DEVICES > ... > Start Monitoring D2C Message] command to monitor the detected messages sent from the BusinessLogicModule to Azure IoT Hub while detecting the target object.  For example:
    ```<language>
    [IoTHubMonitor] [6:56:59 PM] Message received from [peabody11/BusLogicModule]:
    {
      "body": "I see scissors with confidence :: 100",
      "applicationProperties": {
        "MessageSender": "BusinessLogicModule"
      }
    }
    ```

