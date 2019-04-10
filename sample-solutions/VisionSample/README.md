# Deploy Deep Learning Models to Vision AI Developer Kit Using Visual Studio Code

This is a sample showing how to use Azure Machine Learning SDK and Azure IoT Edge to convert a model, build a container image, and deploy a model image to Vision AI Vision AI Developer Kit in Visual Studio Code.

## Setup Visual Studio Code Development Environment

1. Install [Visual Studio Code](https://code.visualstudio.com/Download) (VS Code).

1. Install 64 bit [Anaconda with Python version 3.7](https://www.anaconda.com/distribution), and add Anaconda path to the System PATH environment variable.

1. Install the following extensions for VS Code:
    * [Azure Machine Learning](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.vscode-ai) ([Azure Account](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account) and the [Microsoft Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) will be automatically installed)
    * [Azure IoT Hub Toolkit](https://marketplace.visualstudio.com/items?itemName=vsciot-vscode.azure-iot-toolkit)
    * [Azure IoT Edge](https://marketplace.visualstudio.com/items?itemName=vsciot-vscode.azure-iot-edge) 

1. Restart VS Code.

1. Select **[View > Command Palette…]** to open the command palette box, then enter **[Python: Select Interpreter]** command in the command palette box to select your Python interpreter.

1. Enter **[Azure: Sign In]** command in the command palette box to sign in Azure account and select your subscription.

1. Create a new IoT Hub and a new IoT Edge device in VS Code as mentioned in [Create an IoT Hub using the Azure IoT Hub Toolkit for VS Code](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-create-use-iot-toolkit) and [Register a new Azure IoT Edge device from VS Code](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-register-device-vscode#create-a-device).

1. Create a new workspace in VS Code as mentioned in [Get started with Azure Machine Learning for VS Code](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-vscode-tools#get-started-with-azure-machine-learning). Or use the **00-aml-configuration.py** script described in the next section to create a new resource group and a new workspace.

    > Note: Must use the **East US** region.

## Deploy a Model Container Image in VS Code

1. Download the latest VS Code sample from <https://github.com/Microsoft/vision-ai-developer-kit/tree/master/sample-solutions/VisionSample> and expand it.

1. Launch VS Code, and select **[File > Open Folder…]** command to open the **VisionSample** directory as workspace root.

1. Use **[Python: Select Interpreter]** command in the command palette box or click the current **Python interpreter** option on the bottom line to set **python.pythonPath** in .vscode\settings.json.

1. Launch VS Code by "Run as administrator". Select **[Terminal > New Terminal]** command to open a terminal window, change directory to **MachineLearning\scripts**, and execute `pip install --upgrade -r requirements.txt` to install required Python packages.

1. Open **00-aml-configuration.py** under the MachineLearning\scripts folder and replace the 3 fake settings to your Azure Machine Learning Service Workspace settings.

1. Click **[Run Below]** link on the top line of 00-aml-configuration.py. It will create a new workspace or a new resource group if they don’t exist, and it will write a config.json file under the aml_config folder.

1. Open **01-convert-model-containerize.py** under the MachineLearning\scripts folder and click **[Run Cell | Run Above | Run Below]** link to register the model, convert the model, create a container image, and write settings related to the container image to the .env file under the DeployContainerFromAML folder.
    > Note:
    >   * **01-convert-model-containerize.py** script will import settings from **current_config.py** file in **MachineLearning\scripts\model_configs** folder.  So, this script can be reused to create container image for different model by changing **current_config.py**'s content.
    >   * When change to process a different model, remember to click **Restart** button on the top line in **Python Interactive** window to restart **iPython kernel** to prevent unexpected cache error.

1. Right-click **deployment.template.json** file under the DeployContainerFromAML folder and select **[Generate IoT Edge Deployment Manifest]** command to create a new deployment.json file under the DeployContainerFromAML\config folder.

1. Click **[Explorer]** icon, click **[…]** at **[AZURE IOT HUB DEVICES]** section right side, and select **[Select IoT Hub]** command to select an IoT Hub.

1. Expand **[AZURE IOT HUB DEVICES]** section, right-click an IoT Edge device, select **[Create Deployment for Single Device]** command, select **deployment.json** file under the DeployContainerFromAML\config folder, and click the **[Select Edge Deployment Manifest]** button to deploy the container image to the IoT Edge device.

1. Setup the Vision AI Developer Kit to connect to the IoT Edge device and deploy the module image.

1. Monitor the deployment status for the Vision AI Developer Kit by using platform tools commands: `adb shell docker ps` and `adb shell docker logs edgeAgent -f` commands.
    > Note: The maximum count of images (excluding azureiotedge-hub and azureiotedge-agent) in a device is 3. Use `adb shell docker images` command to check the count of container images deployed to the device and use `adb shell docker rmi <*IMAGE ID*>` command to delete useless images.

1. Check image classification results:
    * mobilenet-imagenet model can detect 1000 image classes listed in the **MachineLearning\models\mobilenet-imagenet\orig\output_labels.txt**.
    * Use platform tools commands `adb shell docker logs <*image name*>` to check container image outputs.
    * Select **[AZURE IOT HUB DEVICES > … > Select IoT Hub]** command and **[AZURE IOT HUB DEVICES > … > Start Monitoring D2C Message]** command to monitor the messages sent from the Vision AI Developer Kit to Azure IoT Hub.

## Retrain MobileNet V1 Classification Model

1. Retrain the MobileNet V1 model with the soda_cans dataset on cloud:
    * Open **02-mobilenet-transfer-learning-cloud.py** and click **[Run Cell | Run Above | Run Below]** link to retrain a new MobileNet V1 model on cloud with soda_cans dataset in the MachineLearning\data\soda_cans folder.
    * After the script execution finished, it will write a va-snpe-engine-library_config.json config file to the MachineLearning\models\mobilenet-retrain-cloud/outputs folder and overwrite current_config.py content by mobilenet_retrain_cloud_config.py in the MachineLearning\scripts\model_configs folder.
    * Repeat step 7 and 8 in **[Deploy a Model Container Image in VS Code]** section to open and execute `01-convert-model-containerize.py` to convert model, create container image, and generate deployment.json for deploying the new MobileNet V1 model retrained on soda_cans dataset.

1. Retrain the MobileNet V1 model with poker6 dataset on a local machine:
    * Open **03-mobilenet-transfer-learning-local.py** and click **[Run Cell | Run Above | Run Below]** link to retrain a new MobileNet V1 model on a local machine with poker6 dataset in the MachineLearning\data folder.
    * After the script execution finished, it will write a va-snpe-engine-library_config.json config file to the MachineLearning\models\mobilenet-retrain-local folder and overwrite current_config.py content by mobilenet_retrain_local_config.py in the MachineLearning\scripts\model_configs folder.
    * Repeat step 7 and 8 in **[Deploy a Model Container Image in VS Code]** section to open and execute `01-convert-model-containerize.py` to convert the model, create container image, and generate deployment.json for deploying the new MobileNet V1 model retrained on poker6 dataset.

## Retrain MobileNet V1 SSD Object Detection Model

Refer to [MachineLearning/ssd_sample/README.md](./MachineLearning/ssd_sample/README.md) for more detail.

## Deploy a Caffe2 Model

1. A Caffe2 model sample in MachineLearning/models/caffe_v2_fork_scissors.

1. Overwrite current_config.py content by `caffe_v2_fork_scissors.py` in the MachineLearning\scripts\model_configs folder.

1. Repeat step 7 and 8 in **[Deploy a Model Container Image in VS Code]** section to open and execute `01-convert-model-containerize.py` to convert the model, create a container image, and generate deployment.json for deploying the Caffe2 model.

## Develop and Deploy a Classification Model using Azure Custom Vision Service

* What you will need...
  * A valid Azure subscription. Create an account for free.
  * A set of images for use in training your classifier.

1. Using a browser, login to the Azure Custom Vision Service at <https://www.customvision.ai>.
    > Note: Please review the Teams Wiki for pre-GA access details.

1. Follow these instructions for [How to build a classifier with Custom Vision](https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/getting-started-build-a-classifier). When creating a new project, use these recommended settings for the Vision AI Dev Kit hardware.
   * Project Type - [Classification]
   * Classification Type - [Multiclass (Single tag per image)]
   * Domain - [General(compact)]

1. After the model is built, click **Export** button in the Performance tab of the <https://www.customvision.ai> portal, and download the trained vision model for the Vision AI DevKit.

1. Copy the exported **model.dlc** and **labels.txt** files to the MachineLearning\CreateAndDeployEdgeContainer\modules\VisionSampleModule\model folder.

1. Copy **va-snpe-engine-library_config.json** file from MachineLearning\models\caffe_v2_fork_scissors folder to the MachineLearning\CreateAndDeployEdgeContainer\modules\VisionSampleModule\model folder.

1. Refer to [MachineLearning/CreateAndDeployEdgeContainer/README.md](./CreateAndDeployEdgeContainer/README.md) to build a local container image and deploy the exported Azure Custom Vision model.
