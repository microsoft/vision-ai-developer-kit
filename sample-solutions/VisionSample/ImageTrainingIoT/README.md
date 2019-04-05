# Device IoT Setup and Deployment

Thursday, March 14, 2019 3:51 PM

## Prerequisites

1. Environment Setup - Refer to CustomVisionImageTraining/README.md
1. Model Train - Refer to CustomVisionImageTraining/README.md
1. Model Download - Download DLC files and unzip
1. Have a Microsoft Account to access <https://azure.github.io/Vision-AI-DevKit-Pages/docs/Get_Started/>
1. Create a new or use existing Azure Portal Account <https://portal.azure.com>
1. "What you will need and will do": <https://azure.github.io/Vision-AI-DevKit-Pages/docs/Deploy_Model_IoT_Hub/#>
1. Python Tutorial and prerequisites: <https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module>

## Quick Start - Run AR Camera Local (without IoT Edge Hub)

1. Go to modules\VisionSampleModule Folder
1. Start a terminal and run python(3) command
- python python_iotcc_sdk\sdk\capture_and_train.py -t Pen -n 10
- -t Pen is tag name
- -n 10 is the number of images to be captured

## Instructions

1. Open Azure Portal Dashboard, create an IoT Hub with minimum "S1" standard tier to manage devices <https://azure.microsoft.com/en-us/services/iot-hub/;>
1. Register devices to Azure IoT Edge from the Azure
   - <https://docs.microsoft.com/en-us/azure/iot-edge/how-to-register-device-portal>
1. Flash Camera firmware: <https://azure.github.io/Vision-AI-DevKit-Pages/docs/Firmware/#>
   - Software release website (TBD)
1. Connect camera device with Azure Register Container
   - <https://azure.github.io/Vision-AI-DevKit-Pages/>
1. Clone project: <https://github.com/Microsoft/vision-ai-developer-kit>
1. Copy/move trained model into folder:
   - vision-ai-developer-kit\sample-solutions\VisionSample\IoTEdgeSolution\modules\VisionSampleModule\model
   - The folder contains:
      1. labels.txt - image tag
      1. model.dlc - the trained knowledge file
      1. va-snpe-engine-library_config.json - engine config file
1. In VS Code, open the project folder **vision-ai-developer-kit\sample-solutions\IoTEdgeSolution\modules\VisionSampleModule\python_iotcc_sdk\sdk**
   1. Edit modules\VisionSampleModule\module.json
      - Change "repository": "the url of container registry".
         - Example:

           ```json
           "repository": "mycapreg.azurecr.io/visionsamplemodule"
           ```

      - Also change config\deployment.json.
         - Example:

            ```json
            "registryCredentials": {
              "mycapreg": {
              "username": "$CONTAINER_REGISTRY_USERNAME",
              "password": "$CONTAINER_REGISTRY_PASSWORD",
              "address": "$CONTAINER_REGISTRY_ADDRESS"
            }
            ```

   1. Edit modules\.env from Azure Container Registry
      - See <https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry>
      - Example:

         ```.env
         CONTAINER_REGISTRY_USERNAME=""
         CONTAINER_REGISTRY_PASSWORD=""
         CONTAINER_REGISTRY_ADDRESS= "xxx.azurecr.io"
         ```

   1. In the left panel, select "Docker Container Register" Login.
   1. Find "deployment.template.json (same folder as README.md).
       - Right-click and choose **Build and Push IoT Solution**.
   1. In "config" folder find the file **deployment.json**, right-click it, and choose **Deploy to device**.
1. Troubleshooting steps at <https://visionaidevkitsupport.azurewebsites.net/>.
