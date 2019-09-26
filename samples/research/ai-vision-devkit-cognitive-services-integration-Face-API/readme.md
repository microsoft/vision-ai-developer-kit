# Develop and Deploy a New AIVisionDevKitFaceAPIModule for Vision AI Developer Kit

This solution is used to build and deploy a new AIVisionDevKitFaceAPIModule developed by QTI's python SDK to Vision AI Developer Kit.

## Setup Build Environment

1. Refer to the "Setup Visual Studio Code Development Environment" section in [VisionSample README.md](../../VisionSample/README.md) to setup a build environment.

1. Install [Docker Community Edition (CE)](https://docs.docker.com/install/#supported-platforms). Don't sign in to Docker Desktop after Docker CE is installed.

1. Install [Docker Extension](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker) to Visual Studio Code.
    - `code --install-extension peterjausovec.vscode-docker`

## Develop a New AIVisionDevKitFaceAPIModule

Refer to [modules/AIVisionDevKitFaceAPIModule/python_iotcc_sdk/README.md](modules/AIVisionDevKitFaceAPIModule/python_iotcc_sdk/README.md) to develop and test source code for a new AIVisionDevKitFaceAPIModule.

## Build a Local Container Image for AIVisionDevKitFaceAPIModule

1. Launch Visual Studio Code, and select **File > Open Folder...** command to open the IotEdgeSolution directory as workspace root.

1. Update the .env file with the values for your container registry. Refer to [Create a container registry](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry) for more detail about ACR settings. [Create a Cognitive Services Account](https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesFace). Refer to [Quickstart: Create a Cognitive Services account in the Azure portal](https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-apis-create-account) for more informtaion.

     ```bash
     REGISTRY_NAME=<YourAcrUri>
     REGISTRY_USER_NAME=<YourAcrUserName>
     REGISTRY_PASSWORD=<YourAcrPassword>
     FACE_API_URL=<YourFaceAPIURL>
     FACE_API_SUBSCRIPTION_KEY=<YourFACEAPISubscriptionKey>
     CAMERA_IP=<CameraIP-Only needed to use _test_local function>
     ```

1. Sign in to your Azure Container Registry by entering the following command in the Visual Studio Code integrated terminal (replace <REGISTRY_USER_NAME> to your container registry user name set in the .env file).
    - `az acr login --name <REGISTRY_USER_NAME>`

1. Copy the files DLC, labels.txt, and va-snpe-engine-library_config.json to the modules\AIVisionDevKitFaceAPIModule\model folder.

1. Open modules\AIVisionDevKitFaceAPIModule\module.json and change the version setting in the tag property for creating a new version of the module image.

1. Right-click on deployment.template.json and select the **Build and Push IoT Edge Solution** command to generate a new deployment.json file in the config folder, build a module image, and push the image to the specified ACR repository.
    > Note: Some red warnings "/usr/bin/find: '/proc/XXX': No such file or directory" and "debconf: delaying package configuration, since apt-utils is not installed" displayed during the building process can be ignored.

1. Right-click on config/deployment.json, select **Create Deployment for Single Device**, and choose the targeted IoT Edge device to deploy the container image.

1. When a person is detected a image capture will be sent to the Azure Face API for detection. The results can be viewed at http://**CameraIP**:1080/media/Azure_Face_Api_Result.jpg and http://**CameraIP**:1080/media/Azure_Face_Api_Result.json

1. You'll find troubleshooting steps at <https://visionaidevkitsupport.azurewebsites.net/>.