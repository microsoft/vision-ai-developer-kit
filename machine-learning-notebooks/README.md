## Getting started with Jupyter Notebooks in Azure
Setup a NotebookVM in Azure Machine Learning Workspace.
1. If you have an Azure Machine Learning service workspace, skip to step #2. Otherwise, create one now.
   - Sign in to the [Azure portal](https://portal.azure.com) by using the credentials for the Azure subscription you use.
   - In the upper-left corner of the portal, select __Create a resource__.
   - In the search bar, enter __Machine Learning__. Select the __Machine Learning service workspace__ search result.
   - In the __ML service workspace__ pane, scroll to the bottom and select Create to begin.
   - In the __ML service workspace__ pane, configure your workspace and select __Create__. It can take a few minutes to create the workspace. When the process is finished, a deployment success message appears. It's also present in the notifications section. To view the new workspace, select __Go to resource__.

2. Create a cloud-based notebook server.
   - Open your Machine Learning workspace in the Azure portal.
   - On your workspace page in the Azure portal, select __Notebook VMs__ on the left.
   - Select __+New__ to create a notebook VM.
   - Provide a name for your VM and select __Create__.
   - Wait approximately 4-5 minutes until the status changes to __Running__
3. Launch the Jupyter wed interface in your Notebook VM
   - Select __Jupyter__ in the __URI__ column for your VM.
   - On the Jupyter notebook webpage, the top foldername is your username.
   
More details about quickstart setup instructions are located [here](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-run-cloud-notebook).

### Clone this repo to your Notebook VM
From the Notebook VM launch the Jupyter web interface as descriped in step #3 above. Click New -> Terminal on the upper right corner of the web interface. You will get a new browser tab with the bash prompt. 
You can use regular `git clone --recursive https://github.com/microsoft/vision-ai-developer-kit` command line commands to clone this repository into a desired folder.

**Important** update _jupyter_ in the Notebook VM: _(this is a temporary step)_

`pip install –upgrade notebook`

`sudo -i systemctl restart jupyter`

Select a notebook in `machine-learning-reference\notebooks` to run it. Set the kernel to **Python 3.6 - AzureML**.

## Notebooks in this repo
The `00-aml-configuration.ipynb` contains the basic steps to setup the environment for Azure ML. _This step is important to complete your `config.json` file_

There are 4 notebooks in this folder as sample tutorials for the Vision AI Developer Kit.
`01-convert-model-containerize.ipynb` uses a pretained Mobilenet/Tensorflow model to convert and deploy on the Vision AI Dev Kit.
`02-mobilenet-transfer-learning` shows a transfer learning example to deploy the Mobilenet model on the Vision AI Dev Kit device.
`03-squeezenet-custom-vision.ipynb` converts a model that is imported from CustomVision.ai.
`04-Deploy-Trained-Model.ipynb` is an example to deploy a trained model to an existing IoT Edge device. 

Also find other quickstarts and how-tos on the [official documentation site for Azure Machine Learning service](https://docs.microsoft.com/en-us/azure/machine-learning/service/).
