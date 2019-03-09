*** The README Instruction contains 2 parts ***
*** Part 1: Instruction for Training Vision Models using Azure Machine Learning Vision Cognitive ***
*** Part 2: Instruction for Register and Upload Model files ***
Author: v-fecui@microsoft.com

Part 1 - Training Models
	1.1 Prepare Account and Azure Vision Machine Learning API documents
	Custom Vision API Document locates at 
	https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/

	How to Create Account and Get Started Guide at
	https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/getting-started-build-a-classifier

	1.2 Prepare Image files
	Image samples are located at "images" folder

	1.3 Sample python scripts
	Python scripts are located at "python" folder
	
	1.4 Azure Machine Learning Environment Setup
	__init__.py contains azure subscription key and env, users shall change it
	Note:
	Please use "eastus" Azure region when open Azure Workspace
	"eastus" Azure region is tested well for model register and model convertion; others may have pending issues
	
	1.5 Model Training - custom_vision_training_sample.py

Part 2 - Azure Workspace Creation and Model Register
	2.1 Workspace Creation, Workspace retriever and Model Register using 
	azure_workspace_sample.py
	
	2.2 Model download script does NOT work due to Azure Model platform existing issue