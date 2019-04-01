
# The README Instruction

> Note: This is a demo project to show you how to create custom vision model files

## Prerequisites

Account at <https://www.customvision.ai/projects>.
Instructions at <https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/python-tutorial>.

## Part 1: Vision AI Environment Setup

This notes provide instructions "How to setup Azure Vision AI Environment"

### Windows 10

1. Install Python 3.7+
   - Download Python 3.7+ software at <https://www.python.org>.
   - "How to" document at <https://docs.python.org/3/>.
1. Install Git
   - Download Git software at <https://git-scm.com/downloads>.
   - "How to" install in windows exe at <https://git-scm.com/download/win>.
   - Optional instructions:
      - <https://www.onlinetutorialspoint.com/git/how-to-install-git-windows-10-operating-system.html>.
      - <https://cs.hofstra.edu/docs/pages/guides/git_win_install.html>.
1. Python Visual Studio Code
   - <https://code.visualstudio.com/docs/languages/python>.
   - Tutorial at <https://code.visualstudio.com/docs/python/python-tutorial>.

1. Open "Windows PowerShell" or "Command Prompt" with "Run as administrator"
   - Reference guide can be found at <https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/python-tutorial>
   - pip package: https://pypi.org/project/azure-cognitiveservices-vision-customvision/1.0.0/

  To install the vision AI libraries, type `pip install azure-cognitiveservices-vision-customvision==1.0.0`

### Linux/iOS

1. Login to Ubuntu or Ubuntu VM version 18.04.
1. Install and configure development software.
   1. Install the build tools.

      ```terminal
      sudo apt-get install build-essential checkinstall
      sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev
         \ libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
      sudo apt-get install libffi-dev
      ```

   1. Download Python 3.7.2.

      ```terminal
      cd /usr/src
      sudo wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz
      ```

   1. Extract tgz: `sudo tar xzf Python-3.7.2.tgz`
   1. Compile.

      ```terminal
      cd Python-3.7.2
      sudo ./configure --enable-optimizations
      sudo make altinstall
      ```

   1. Add alias into ~/.bashrc: `alias python='/usr/local/bin/python3.7m'`
   1. Install pip:

       ```terminal
       curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
       sudo python get-pip.py
       sudo pip install --upgrade pip
       ```

The following steps are the same as Windows users (use sudo for admin users). Optionally use PyCharm or Intellij Community SDK

## Part 2 - Training Models

1. Azure Vision Machine Learning API documents and Custom Vision API Document locates at <https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/>.
   - How to Create Account and Get Started Guide at <https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/getting-started-build-a-classifier>.
1. Prepare Image files
   - Image samples are located in the **images** folder

   ![alt text](folder.PNG)
1. Start VS Code and open folder **vision-ai-developer-kit/sample-solutions/VisionSample/CustomVisionImageTraining**
   - Sample python scripts are located in the **python** folder
1. Sign in at <https://www.customvision.ai/projects> and click the settings icon to get your training key and endpoint
   - Or use the testing site at <https://iris-demo1.azurewebsites.net/>
   - Modify **__init__.py** in the python folder (contains vision AI training keys)

      ```python
      TRAINING_KEY = "<place training key here>"
      TRAINING_ENDPOINT = "<e.g. https://irisdemo1.azure-api.net/customvision/v3.0/Training/>"
      ```

   ![alt text](project.PNG)
1. Save changes and right click - custom_vision_training_sample.py
   - Run Python File in Terminal
1. Go to project <https://www.customvision.ai/projects>
   - Download trained model files
   > Note: DLC file can only be downloaded at test site <https://iris-demo1.azurewebsites.net/>
1. Deploy this model on the IoTEdgeSolution Project. Please read the project [../IoTEdgeSolution/README.md](../IoTEdgeSolution/README.md)
