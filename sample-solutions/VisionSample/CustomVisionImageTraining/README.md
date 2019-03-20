*** The README Instruction ***

*** Part 1: Vision AI Environment Setup ***
*** Part 2: Instruction for Training Vision Models using Azure Machine Learning Vision Cognitive ***

Author: v-fecui@microsoft.com

Thursday, March 14, 2019
2:16 PM

Part 1: Vision AI Environment Setup

This notes provide instructions "How to setup Azure Vision AI Environment"

Windows 10:

	1. Install Python 3.7+
	Download Python 3.7+ software at https://www.python.org
	How to document at https://docs.python.org/3/

	2. Install Git
	Download Git software at https://git-scm.com/downloads
	How to install in windows exe at
	https://git-scm.com/download/win
	Optional instruction:
	https://www.onlinetutorialspoint.com/git/how-to-install-git-windows-10-operating-system.html
	https://cs.hofstra.edu/docs/pages/guides/git_win_install.html


	3. Python Visual Studio Code
	https://code.visualstudio.com/docs/languages/python
	Tutorial at
	https://code.visualstudio.com/docs/python/python-tutorial

	4. Open "Windows PowerShell" or "Command Prompt" with "run as administrator"
	Reference guide can be found at https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/python-tutorial

	4.1 install AzureML SDK
	>pip install --upgrade azureml-sdk

	4.2 install Azure vision libraries, type command
	> pip install --upgrade azure-cognitiveservices-vision-customvision

	4.2 install Azure vision core libraries, type command https://pypi.org/project/azure-storage/
	>pip install --upgrade azure-storage

	4.3 Optional Google Image URL download tool:
	>pip install --upgrade google_images_download


Linux/iOS:
	1. Login Ubuntu or Ubuntu VM version 18.04;

	2. Default Python maybe 3.5 or 3.6. Install Python 3.7.2:
	2.1 install build tools:
		$sudo apt-get install build-essential checkinstall
		$sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev \
		    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
		$sudo apt-get install libffi-dev

	2.2 Download python 3.7.2:
		$cd /usr/src
		$sudo wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz

	2.3 Extract tgz:
		$sudo tar xzf Python-3.7.2.tgz

	2.4 Compile:
		$cd Python-3.7.2
		$sudo ./configure --enable-optimizations
		$sudo make altinstall

	2.3 Add alias into ~/.bashrc
		alias python='/usr/local/bin/python3.7m'

	3. Install pip:
		$curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
		$sudo python get-pip.py
		$sudo pip install --upgrade pip

	4. Following steps same as Windows users (use sudo for admin users)
	Optional use PyCharm or Intellij Community SDK


Part 2 - Training Models
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
	__init__.py contains azure subscription key
	SUBSCRIPTION_KEY_ENV_NAME = "training id"

	Note:
	Please use "eastus" Azure region when open Azure Workspace
	"eastus" Azure region is tested well for model register and model convertion; others may have pending issues
	
	1.5 Model Training Sample- custom_vision_training_sample.py
