# Setup VS Code Development Environment

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

8. Create a new workspace in VS Code as mentioned in Get started with Azure Machine Learning for Visual Studio Code.  Or use **00-aml-configuration.py** script described in the next section to create a new resource group and a new workspace.

Note: Must use the region listed in the supported regions for Azure Machine Learning service to create a new workspace.
