# Develop and deploy an IoT Edge module OnnxRuntimeModule

onnxruntime-sample IoT Edge solution sample is used to demo how to build and deploy an ONNX Runtime module.  This sample will input camera preview RTSP stream, detect objects by a Tiny YOLO V2 ONNX model, and save the detection result result.jpg to the /data/misc/qmmf folder under CPU mode.

## Setup Build Environment

1. Refer to [**Setup Visual Studio Code Development Environment**] section in [VisionSample README.md](../VisionSample/README.md) to setup build environment.

1. Install [**Docker Community Edition (CE)**](https://docs.docker.com/install/#supported-platforms).  Don't sign in **Docker Desktop** after Docker CE installed.

1. Install [**Docker Extension**](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker) to **Visual Studio Code**.

## Build a Local Container Image with a Single Module: OnnxRuntimeModule

modules\\**OnnxRuntimeModule** folder includes:
   * **app** folder: source code used to detect objects.
       * main.py: is used to detect objects by a [Tiny YOLOv2 ONNX model](https://onnxzoo.blob.core.windows.net/models/opset_8/tiny_yolov2/tiny_yolov2.tar.gz) from [ONNX Model Zoo](https://github.com/onnx/models).
       * main_yolov3.py: is used to detect objects by a [YOLO V3 ONNX model](https://onnxzoo.blob.core.windows.net/models/opset_10/yolov3/yolov3.tar.gz) from [ONNX Model Zoo](https://github.com/onnx/models).
   * **Dockerfile.arm32v7** file: instructions used to build container image.
       * `CMD ["python3", "-u", "main.py"]` command is used to run Tiny YOLOv2 ONNX model detection.
       * `CMD ["python3", "-u", "main_yolov3.py"]` command is used to run YOLO V3 ONNX model detection.
   * **module.json** file: config file for this module.

1. Launch **Visual Studio Code**, open folder to onnxruntime-sample located folder, and set Default Platform to be **arm32v7**.

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
    * Use `adb shell ifconfig wlan0` command to get the camera's wireless IP address or find the IP address from **rtst_addr** property shown in OnnxRuntimeModule's **Module Identity Twin** page.
    * Open a browser to browse http://CAMERA_IP:1080/media/result.jpg or http://CAMERA_IP:1080/media/result.html (using Edge to auto refresh result.jpg) where CAMERA_IP is the camera's IP address you found above.
    * Or execute `python show_result.py "http://CAMERA_IP:1080/media/result.jpg"` command from **onnxruntime-sample\modules\OnnxRuntimeModule\test** folder to display the detection result in an OpenCV window.  Type 'q' key in the OpenCV window to quit show_result.py.
    * A detection result sample is shown in **onnxruntime-sample\modules\OnnxRuntimeModule\test\result.jpg**.

> **Note:**
> * This is a POC sample and its purpose is used to prove ONNX Runtime package can be installed on Vision AI DevKit, and it can use ONNX Runtime APIs to load ONNX models from ONNX Model Zoo and detect objects by the images captured from Vision AI DevKit.  So we will ignore the following unstable/lag/delay issues and focus on the detection results:
>     * Currently there is no API can be used to capture frames from camera directly in the current Camera SDK, so this sample capture frames from camera's preview RTSP stream.  And it needs to use a faster WiFi connction, otherwise cv2.VideoCapture() will read RTSP stream fail and need to be re-initialized frequently caused by the RTSP sream is not stable.
>     * Currently there is no API can be used to draw labels and bounding boxes to HDMI display directly, so this sample saves the detection result to a disk file and the result content update will be delayed about 5 to 10 sec longer than the preview.
>     * The detection accruacy for YOLO V3 model is better than YOLO V2 model, but YOLO V3's inference rate 0.15 fps is much slower than YOLO V2's 1 fps.  So it's better to run YOLO V3 model under DSP mode in the future. Check [result_yolov3.jpg](./modules/OnnxRuntimeModule/test/result_yolov3.jpg) vs [result_tinyyolov2.jpg](./modules/OnnxRuntimeModule/test/result_tinyyolov2.jpg).

