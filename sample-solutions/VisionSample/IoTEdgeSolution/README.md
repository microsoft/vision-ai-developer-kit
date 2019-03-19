Device IoT Setup and Deployment

Thursday, March 14, 2019
3:51 PM

Prerequisites:
	1. Environment Setup in AMLImageTraining Folder README.md
	2. Model Train
	3. Model Download
	4. Have a Microsoft Account to access Github project and https://azure.github.io/Vision-AI-DevKit-Pages/docs/Get_Started/
	5. Azure Portal Account https://portal.azure.com

*** Instructions ***
	1. Open Azure Portal Dashboard, create an IoT Hub with minimum "S1" standard tier to manage devices https://azure.microsoft.com/en-us/services/iot-hub/;

	2. Register Camera as IoT Edge device from the Azure
	https://docs.microsoft.com/en-us/azure/iot-edge/how-to-register-device-portal


	3. Flash Camera firmware: https://azure.github.io/Vision-AI-DevKit-Pages/docs/Firmware/#
	Software release website (TBD)

	4. Android Debug Bridge (ADB) and Fastboot Tools
	Tools are Included into Android Studio and SDK tool https://developer.android.com/studio

	5. Clone project: https://github.com/Microsoft/vision-ai-developer-kit

	6. Download " Vision AI Dev Kit" model
    From https://iris-demo1.azurewebsites.net/projects/

   	7. copy/move trained model into folder:
	vision-ai-developer-kit\sample-solutions\VisionSample\IoTEdgeSolution\modules\VisionSampleModule\model
	The folder contains:
	7.1 labels.txt - image tag
	7.2 model.dlc - the trained knowledge file
	7.3 va-snpe-engine-library_config.json - engine config file
	(review values: "Engine":2, … "ScaleWidth":227, "ScaleHeight":227 …)
	The values were set in Model Train configures

	8. Visual Studio Code open project folder:
	vision-ai-developer-kit\sample-solutions\VisionAiDevKit
	8.1 edit modules\VisionSampleModule\.env to your Azure IoT Hub
	Example:
	CONTAINER_REGISTRY_USERNAME=""
	CONTAINER_REGISTRY_PASSWORD=""
    CONTAINER_REGISTRY_ADDRESS= "xxx.azurecr.io"
