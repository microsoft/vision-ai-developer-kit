# Develop and Deploy a New VisionSampleModule for Vision AI Developer Kit 

This solution is used to build and deploy a new VisionSampleModule developed by QTI's python SDK to Vision AI Developer Kit.

## Setup Build Environment

1. Refer to [**Setup Visual Studio Code Development Environment**] section in [VisionSample README.md](../../VisionSample/README.md) to setup build environment.

1. Install [**Docker Community Edition (CE)**](https://docs.docker.com/install/).  Don't sign in **Docker Desktop** after Docker CE installed.

1. Install [**Docker Extension**](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker) to **Visual Studio Code**.


## Develop a New VisionSampleModule

Refer to [modules/VisionSampleModule/python_iotcc_sdk/README.md](modules/VisionSampleModule/python_iotcc_sdk/README.md) to develop and test source code for a new **VisionSampleModule**.

## Build a Local Container Image for VisionSampleModule

1. Launch Visual Studio Code, and select **[File > Open Folder…]** command to open the **IotEdgeSolution** directory as workspace root.

1. Update the **.env** file with the values for your container registry.  Refer to [**Create a container registry**](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry) for more detail about ACR settings.
     ```<language>
     REGISTRY_NAME="Your ACR name"
     REGISTRY_USER_NAME="Your ACR username"
     REGISTRY_PASSWORD="Your ACR password"
     ```

1. Sign in **Azure Container Registry** by entering the following command in the **Visual Studio Code** integrated terminal (replace <REGISTRY_USER_NAME>, <REGISTRY_PASSWORD>, and <REGISTRY_NAME> to your container registry values set in the **.env** file):
    ```<language>
    docker login -u <REGISTRY_USER_NAME> -p <REGISTRY_PASSWORD> <REGISTRY_NAME>.azurecr.io  
    ```
1. Copy **DLC** file and its related **labels.txt** and **va-snpe-engine-library_config.json** to **modules\VisionSampleModule\model** folder.

1. Open **modules\VisionSampleModule\module.json** file and change **version** setting in **tag** property for creating a new version of the module image.

1. Right-clicking on **deployment.template.json** file and select **[Build and Push IoT Edge Solution]** command to generate a new **deployment.json** file in **config** folder, build a module image, and push the image to the specified ACR repository.
    > **Note:** Some red warnings "**/usr/bin/find: '/proc/XXX': No such file or directory**" and "**debconf: delaying package configuration, since apt-utils is not installed**" displayed during the building process can be ignored.

1. Right-clicking on **config/deployment.json** file, select **[Create Deployment for Single Device]**, and choose the targeted IoT Edge device to deploy the container Image.

1. Troubleshooting steps at <https://visionaidevkitsupport.azurewebsites.net/>.