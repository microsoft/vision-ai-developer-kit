# Deploy a Container Image Built by Azure Machine Learning SDK to the Target Device

For deploying the container image built by **MachineLearning\scripts\01-convert-model-containerize.py**.

## Deploy the solution to the target device

1. The values for container image and the container retistry in **.env** file will be updated automatically to the right settings after executing **MachineLearning\scripts\01-convert-model-containerize.py**. 

2. Right-clicking on **deployment.template.json** file and select **[Generate IoT Edge Depolyment Manifest]** command to generate a new **deployment.json** file in **config** folder.

3. Right-clicking on **config/deployment.json** file, select **[Create Deployment for Single Device]**, and choose the targeted IoT Edge device to deploy the container Image.
