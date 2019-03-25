Device IoT Setup and Deployment

Thursday, March 14, 2019
3:51 PM

Prerequisites:
	
	1. Environment Setup - Refer to CustomVisionImageTraining/README.md
	2. Model Train - Refer to CustomVisionImageTraining/README.md
	3. Model Download - Download DLC files and unzip
	4. Have a Microsoft Account to access https://azure.github.io/Vision-AI-DevKit-Pages/docs/Get_Started/
	5. Create a new or use existing Azure Portal Account https://portal.azure.com
	6. "What you will need and will do": https://azure.github.io/Vision-AI-DevKit-Pages/docs/Deploy_Model_IoT_Hub/#
	7. Python Tutorial and prerequisites: https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module

*** Instructions ***

	1. Open Azure Portal Dashboard, create an IoT Hub with minimum "S1" standard tier to manage devices https://azure.microsoft.com/en-us/services/iot-hub/;

	2. Register devices to Azure IoT Edge from the Azure
	https://docs.microsoft.com/en-us/azure/iot-edge/how-to-register-device-portal

	3. Flash Camera firmware: https://azure.github.io/Vision-AI-DevKit-Pages/docs/Firmware/#
	Software release website (TBD)
	
	4. Connect camera device with Azure Register Container
	https://azure.github.io/Vision-AI-DevKit-Pages/

	5. Clone project: https://github.com/Microsoft/vision-ai-developer-kit

    6. copy/move trained model into folder:
	   vision-ai-developer-kit\sample-solutions\VisionSample\IoTEdgeSolution\modules\VisionSampleModule\model
	   The folder contains:
	   6.1 labels.txt - image tag
	   6.2 model.dlc - the trained knowledge file
	   6.3 va-snpe-engine-library_config.json - engine config file

	7. Visual Studio Code open project folder:
	    vision-ai-developer-kit\sample-solutions\IoTEdgeSolution\modules\VisionSampleModule\python_iotcc_sdk\sdk
	    
	    7.1 edit modules\VisionSampleModule\module.json
	    change "repository": "the url of container registry"
	    Example:
	    "repository": "mycapreg.azurecr.io/visionsamplemodule"
	    config\deployment.json change with same. Example:
	    "registryCredentials": {
              "mycapreg": {
                "username": "$CONTAINER_REGISTRY_USERNAME",
                "password": "$CONTAINER_REGISTRY_PASSWORD",
                "address": "$CONTAINER_REGISTRY_ADDRESS"
              }

	    7.2 edit modules\.env from Azure Container Registry
	    https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry
	    Example:
	    CONTAINER_REGISTRY_USERNAME=""
	    CONTAINER_REGISTRY_PASSWORD=""
        CONTAINER_REGISTRY_ADDRESS= "xxx.azurecr.io"

        7.3 In the left panel, "Docker Container Register" Login
        7.4 Find "deployment.template.json (same folder as README.md)
            right click and "Build and Push IoT Solution"
        7.5 In "config" folder, find the "deployment.json", right click and deploy to device
    
    8. Trouble shoot: https://visionaidevkitsupport.azurewebsites.net/
        
            
