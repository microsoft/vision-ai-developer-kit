# Installation

1. Install [Visual Studio Code](https://code.visualstudio.com/Download)

2. Install 64 bit [Anaconda with Python version 3.6.5](https://repo.anaconda.com/archive/Anaconda3-5.2.0-Windows-x86_64.exe), and add Anaconda path to the System PATH environment variable. 

3. Install the following extensions for VS Code:
    * [Azure Machine Learning](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.vscode-ai) ([Azure Account](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account) and the [Microsoft Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) will be automatically installed)
    * [Azure IoT Hub Toolkit](https://marketplace.visualstudio.com/items?itemName=vsciot-vscode.azure-iot-toolkit)
    * [Azure IoT Edge](https://marketplace.visualstudio.com/items?itemName=vsciot-vscode.azure-iot-edge) 

4. Restart Visual Studio Code.

5. Select **[View > Command Palette…]** to open the command palette box, then enter **[Python: Select Interpreter]** command in the command palette box to select your Python interpreter.

6. Enter **[Azure: Sign In]** command in the command palette box to sign in Azure account and select your subscription.

7. Create a new IoT Hub and a new IoT Edge device in VS Code as mentioned in Create an IoT hub using the Azure IoT Hub Toolkit for Visual Studio Code and Register a new Azure IoT Edge device from Visual Studio Code. 

8. Create a new workspace in VS Code as mentioned in Get started with Azure Machine Learning for Visual Studio Code. Or use **00-aml-configuration.py** script described in the next section to create a new resource group and a new workspace.

Note: Must use the region listed in the supported regions for Azure Machine Learning service to create a new workspace.

# Deploy a Model Container Image in VS Code 

1. Download the latest VS Code sample from https://github.com/Microsoft/vision-ai-developer-kit/tree/master/sample-solutions/sample-solution-1 and expand it. 

2. Launch VS Code, and select [File > Open Folder…] command to open **sample-solution-1** directory as workspace root. 

3. Use **[Python: Select Interpreter]** command in the command palette box or click the current **Python interpreter**”** option on the bottom line to set **python.pythonPath** in .vscode\settings.json. 

4. Close VS Code and launch VS Code again by “Run as administrator”. Select **[Terminal > New Terminal]** command to open a terminal window, change directory to **MachineLearning\scripts**, and execute the following commands to install required Python packages: 
    * pip install msgpack==0.6.1
    * pip install --ignore-installed PyYAML==4.2b1
    * pip install --upgrade -r requirements.txt

Note: The above installation steps works for the latest Azure Machine Learning SDK version v1.0.8 and install Python 3.6.5 by [Anaconda with Python version 3.6.5](https://repo.anaconda.com/archive/Anaconda3-5.2.0-Windows-x86_64.exe). If the version of AML SDK, Python, or other packages will be changed in the future, you might have to install or upgrade packages manually. 

5. Open **00-aml-configuration.py** under **MachineLearning\scripts** folder and replace the 3 fake settings to your Azure Machine Learning Service Workspace settings.

6. Click **[Run Cell]** or **[Run All Cells]** link on the top line of the cell. It will create a new workspace if it doesn’t exist and write a **config.json** file under **aml_config** folder. 

7. Open **01-convert-model-containerize.py** under **MachineLearning\scripts** folder and click **[Run Cell]** or **[Run All Cells]** link to register model, convert model, create container image, and write settings related to the container image to **.env** file under **EdgeSolution** folder. 

8. Right click **deployment.template.json** file under **EdgeSolution** folder and select **[Generate IoT Edge Deployment Manifest]** command to create a new **deployment.json** file under **EdgeSolution\config** folder.

9. Click **[Explorer]** icon, click **[…]** at **[AZURE IOT HUB DEVICES]** section right side, and select **[Select IoT Hub]** command to select an IoT Hub. 

10. Expand **[AZURE IOT HUB DEVICES]** section, right-click an IoT edge device, select **[Create Deployment for Single Device]** command, select **deployment.json** file under **EdgeSolution\config** folder, and click **[Select Edge Deployment Manifest]** button to deploy the container image to the IoT edge device. 

11. Setup the Vision AI Developer Kit to connect to the IoT Edge device and deploy the module image. 

12. Monitor the deployment status for the Vision AI Developer Kit by using platform tools commands: **[adb shell]**, **[docker ps]** and **[docker logs edgeAgent]** commands. 

13. Check image classification results: 
    * mobilenet-imagenet model can detect 1000 image classes listed in the **MachineLearning\models\mobilenet-imagenet\orig\output_labels.txt**
    * Use platform tools commands **[adb shell > docker logs *image name*]** to check module image outputs:
    * Select **[AZURE IOT HUB DEVICES > … > Select IoT Hub]** command and **[AZURE IOT HUB DEVICES > … > Start Monitoring D2C Message]** command to monitor the messages sent from the Vision AI Developer Kit to Azure IoT Hub:
