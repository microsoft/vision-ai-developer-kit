# Develop and deploy an IoT Edge module VisionSampleModule

For users already have DLC files, they can build an IoT Edge module **VisionSampleModule** on a local machine, push it to Azure Container Registry (ACR) repository, and deploy it to a device.

## Setup Build Environment
1. Download and install Docker from [**Get Started with Docker**](https://www.docker.com/get-started).  Don't sign in **Docker Desktop** after Docker installed.

2. Install [**Docker Extension**](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker) to **Visual Studio Code**.

## Build a Local VisionSampleModule Image

1. Update the **.env** file with the values for your container image name and container registry.  Refer to [**Create a container registry**](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry) for more detail about ACR settings.
   ```<language>
   MODULE_NAME="Your container image name"
   REGISTRY_NAME="Your ACR name"
   REGISTRY_USER_NAME="Your ACR username"
   REGISTRY_PASSWORD="Your ACR password"
   ```

2. Sign in **Azure Container Registry** by entering the following command in the **Visual Studio Code** integrated terminal (replace <REGISTRY_USER_NAME>, <REGISTRY_PASSWORD>, and <REGISTRY_NAME> to your container registry values set in the **.env** file):
    ```<language>
    docker login -u <REGISTRY_USER_NAME> -p <REGISTRY_PASSWORD> <REGISTRY_NAME>.azurecr.io  
    ```
3. Copy **DLC** file and its related **labels.txt** and **va-snpe-engine-library_config.json** to **modules\VisionSampleModule\model** folder.

4. Open **modules\VisionSampleModule\module.json** file and change **version** setting in **tag** property for creating a new version of the module image.

5. Right-clicking on **deployment.template.json** file and select **[Build and Push IoT Edge Solution]** command to generate a new **deployment.json** file in **config** folder, build a module image, and push the image to the specified ACR repository.
    - **Note:** Some red warnings "**/usr/bin/find: '/proc/XXX': No such file or directory**" and "**debconf: delaying package configuration, since apt-utils is not installed**" displayed during the building process can be ignored.

6. Right-clicking on **config/deployment.json** file, select **[Create Deployment for Single Device]**, and choose the targeted IoT Edge device to deploy the container Image.
