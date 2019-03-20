Device IoT Setup and Deployment

Thursday, March 14, 2019
3:51 PM

Prerequisites:
	
	1. Environment Setup - Refer to CustomVisionImageTraining Folder README.md
	2. Model Train - Refer to CustomVisionImageTraining project
	3. Model Download - Download DLC files and unzip
	4. Have a Microsoft Account to access https://azure.github.io/Vision-AI-DevKit-Pages/docs/Get_Started/
	5. Azure Portal Account https://portal.azure.com

*** Instructions ***

	1. Open Azure Portal Dashboard, create an IoT Hub with minimum "S1" standard tier to manage devices https://azure.microsoft.com/en-us/services/iot-hub/;

	2. Register devices to Azure IoT Edge from the Azure
	https://docs.microsoft.com/en-us/azure/iot-edge/how-to-register-device-portal

	3. Flash Camera firmware: https://azure.github.io/Vision-AI-DevKit-Pages/docs/Firmware/#
	Software release website (TBD)
	
	4. Connect camera device with IoT Register Container
	https://azure.github.io/Vision-AI-DevKit-Pages/
	
	Android Debug Bridge (ADB) and Fastboot Tools
	Tools are Included into Android Studio and SDK tool https://developer.android.com/studio

	5. Clone project: https://github.com/Microsoft/vision-ai-developer-kit

	6. Download " Vision AI Dev Kit" model
    From Custom Vision AI - refer to CustomVisionImage Train project
    https://iris-demo1.azurewebsites.net/projects/

   	7. copy/move trained model into folder:
	   vision-ai-developer-kit\sample-solutions\VisionSample\IoTEdgeSolution\modules\VisionSampleModule\model
	   The folder contains:
	   7.1 labels.txt - image tag
	   7.2 model.dlc - the trained knowledge file
	   7.3 va-snpe-engine-library_config.json - engine config file

	8. Visual Studio Code open project folder:
	    vision-ai-developer-kit\sample-solutions\VisionAiDevKit
	    
	    8.1 edit modules\VisionSampleModule\.env from Azure IoT Hub
	    Example:
	    CONTAINER_REGISTRY_USERNAME=""
	    CONTAINER_REGISTRY_PASSWORD=""
        CONTAINER_REGISTRY_ADDRESS= "xxx.azurecr.io"
    
        8.2 In the left panel, "Docker Container Register" Login 
        8.3 Find "deployment.template.json (same folder as README.md)
            right click and "Build and Push IoT Solution"
        8.4 In "config" folder, find the "deployment.json", right click and deploy to device
    
    9. Trouble shoot: https://visionaidevkitsupport.azurewebsites.net/
        
            
