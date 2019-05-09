# Getting started with Jupyter Notebooks in Azure
Setup a NotebookVM in Azure Machine Learning Workspace. The quickstart setup instructions are located [here](https://review.docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-run-cloud-notebook?branch=release-build-amls).

### Clone this repo to your Notebook VM
From the Notebook VM launch the Jupyter web interface. Click New -> Terminal. You will get the bash prompt. 
You can use regular `git clone --recursive https://github.com/microsoft/vision-ai-developer-kit` command line commands to clone this repository into desired folder.

Select a notebook in `machine-learning-reference\notebooks` to run it. Set the kernel to **Python 3.6 - AzureML**.

## Notebooks in this repo
The `00-aml-configuration.ipynb` contains the basic steps to setup the environment for Azure ML.

There are 4 notebooks in this folder as sample tutorials for the Vision AI Developer Kit.
`01-convert-model-containerize.ipynb` uses a pretained Mobilenet/Tensorflow model to convert and deploy on the Vision AI Dev Kit.
`02-mobilenet-transfer-learning` shows a transfer learning example to deploy the Mobilenet model on the Vision AI Dev Kit device.
`03-squeezenet-custom-vision.ipynb` converts a model that is imported from CustomVision.ai.
`04-Deploy-Trained-Model.ipynb` is an example to deploy a trained model to an existing IoT Edge device. 

Also find other quickstarts and how-tos on the [official documentation site for Azure Machine Learning service](https://docs.microsoft.com/en-us/azure/machine-learning/service/).
