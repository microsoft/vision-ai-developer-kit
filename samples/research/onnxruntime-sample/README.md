# Develop and deploy an IoT Edge module OnnxRuntimeModule

Use this IoT Edge solution to build and deploy an ONNX Runtime module to detect objects by a Tiny YOLOv2 ONNX model.

## Setup Build Environment

1. Refer to [**Setup Visual Studio Code Development Environment**] section in [VisionSample README.md](../VisionSample/README.md) to setup build environment.

1. Install [**Docker Community Edition (CE)**](https://docs.docker.com/install/#supported-platforms).  Don't sign in **Docker Desktop** after Docker CE installed.

1. Install [**Docker Extension**](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker) to **Visual Studio Code**.

## Build a Local Container Image with a Single Module: OnnxRuntimeModule

modules\\**OnnxRuntimeModule** folder includes:
   * **app** folder: source code used to detect objects by a [Tiny YOLOv2 ONNX model](https://onnxzoo.blob.core.windows.net/models/opset_8/tiny_yolov2/tiny_yolov2.tar.gz) from [ONNX Model Zoo](https://github.com/onnx/models).
   * **Dockerfile.arm32v7** file: instructions used to build this module image.
   * **module.json** file: config file for this module.

1. Launch **Visual Studio Code**, open folder to onnxruntime-sample located folder, and set Default Platform to be "arm32v7".

2. Update the **.env** file with the values for your container image name and container registry.  Refer to [**Create a container registry**](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry) for more detail about ACR settings.
     ```<language>
     CONTAINER_REGISTRY_NAME="Your ACR address"
     CONTAINER_REGISTRY_USERNAME="Your ACR username"
     CONTAINER_REGISTRY_PASSWORD="Your ACR password"
     ```

3. Sign in **Azure Container Registry** by entering the following command in the **Visual Studio Code** integrated terminal (replace <CONTAINER_REGISTRY_NAME>, <CONTAINER_REGISTRY_USERNAME>, and <CONTAINER_REGISTRY_PASSWORD> to your container registry values set in the **.env** file):
    ```<language>
    docker login <CONTAINER_REGISTRY_NAME> -u <CONTAINER_REGISTRY_USERNAME> -p <CONTAINER_REGISTRY_PASSWORD> 
    ```

4. Open **modules\OnnxRuntimeModule\module.json** file and change **version** setting in **tag** property to create a new version of the module image.

5. Right-clicking on **deployment.template.json** file and select **[Build and Push IoT Edge Solution]** command to generate a new **deployment.arm32v7.json** file in **config** folder, build a module image, and push the image to the specified ACR repository.

6. Right-clicking on **config/deployment.arm32v7.json** file, select **[Create Deployment for Single Device]**, and choose the targeted IoT Edge device to deploy the container Image.

7. Check the detection result:

    * Set your local machine to connect to the same Wi-Fi as Vision AI Dev Kit connecting.
    * Use `adb shell ifconfig wlan0` command to get the camera's wireless IP address or find the IP address from **rtst_addr** property shown in OnnxRuntimeModule's [Module Identity Twin] page.
    * Open a browser to browse http://CAMERA_IP:1080/media/result.jpg or http://CAMERA_IP:1080/media/result.html (auto refresh result.jpg every 2 sec) where CAMERA_IP is the camera's IP address you found above.
    * Or execute `python show_result.py "http://CAMERA_IP:1080/media/result.jpg"` command from **onnxruntime-sample\modules\OnnxRuntimeModule\test** folder to display the detection result in an OpenCV window.

