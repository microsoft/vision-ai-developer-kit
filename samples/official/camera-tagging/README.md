# CameraTaggingModule

## Overview

This repository contains the modules necessary to allow individuals to capture images from an RTSP stream, tag them, and upload them to train a Custom Vision model or simply to a Blob store.

It reads 9 environment variables from which 3 are used to build the default URI to the RTSP stream (i.e. rtsp://<RTSP_IP>:<RTSP_PORT>/<RTSP_PATH>), and 4 are used to describe the local blob store. These environment variables can be specified in the file deployment.template.json.

This module is currently only supports the ARM32 and AMD64 platforms and it does not support the Windows file system.

## Building Container Images

### ARM32

#### Build and push the Client and Server Container Images

Arm32 devices require the base client and server docker images to be built on an arm32 device because certain installation commands are only supported by that platform.

1. Copy over all the folders from **CameraTaggingModule/Arm32Base/** to a folder on an arm32v7 device.

1. Using a command prompt, cd into TaggingClientDocker and run
    - `docker build -t <REGISTRY_NAME>.azurecr.io/<IMAGE_NAME>:<VERSION> .`

1. Push the image to your repository
    - Make sure to first login using `docker login -u <REGISTRY_USER_NAME> -p <REGISTRY_PASSWORD> <REGISTRY_NAME>.azurecr.io`
    - Then push the image using the command `docker push <REGISTRY_NAME>.azurecr.io/<IMAGE_NAME>:<VERSION>`

1. Repeat steps 2 & 3 for TaggingServerDocker.

#### Build a Local Container Image

1. Launch Visual Studio Code, and select **File > Open Folder...** command to open the camera-tagging directory as workspace root.

1. Update the .env file with the values for your container registry. Refer to [Create a container registry](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry) for more detail about ACR settings.

    CONTAINER_REGISTRY_NAME=<Your_Acr_Uri>  
    CONTAINER_REGISTRY_USERNAME=<Your_Acr_UserName>  
    CONTAINER_REGISTRY_PASSWORD=<Your_Acr_Password>  

1. Sign in to your Azure Container Registry by entering the following command in the Visual Studio Code integrated terminal (replace <REGISTRY_USER_NAME>, <REGISTRY_PASSWORD>, and <REGISTRY_NAME> to your container registry values set in the .env file).
    - `docker login -u <REGISTRY_USER_NAME> -p <REGISTRY_PASSWORD> <REGISTRY_NAME>.azurecr.io`

1. Open **CameraTaggingModule/Dockerfile.arm32v7** and change lines 2 and 6 (FROM ...) to reflect the client and server images you just built and pushed.

1. Open **CameraTaggingModule/module.json** and change the version setting in the tag property to create a new version of the module image.

1. Fill in the environment variables found in deployment.template.json 

1. Right-click on deployment.template.json and select the **Build and Push IoT Edge Solution** command to generate a new deployment.json file in the config folder, build a module image, and push the image to the specified ACR repository.
    > Note: Some red warnings "Unknown host QEMU_IFLA type: ##" and "qemu: Unsupported syscall: ##" displayed during the building process can be ignored.

1. Right-click on config/deployment.json, select **Create Deployment for Single Device**, and choose the targeted IoT Edge device to deploy the container image.

1. You'll find troubleshooting steps at <https://visionaidevkitsupport.azurewebsites.net/>.

### AMD64

1. Launch Visual Studio Code, and select **File > Open Folder...** command to open the camera-tagging directory as workspace root.

1. Update the .env file with the values for your container registry. Refer to [Create a container registry](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module#create-a-container-registry) for more detail about ACR settings.

    CONTAINER_REGISTRY_NAME=<Your_Acr_Uri>  
    CONTAINER_REGISTRY_USERNAME=<Your_Acr_UserName>  
    CONTAINER_REGISTRY_PASSWORD=<Your_Acr_Password>    

1. Sign in to your Azure Container Registry by entering the following command in the Visual Studio Code integrated terminal (replace <REGISTRY_USER_NAME>, <REGISTRY_PASSWORD>, and <REGISTRY_NAME> to your container registry values set in the .env file).
    - `docker login -u <REGISTRY_USER_NAME> -p <REGISTRY_PASSWORD> <REGISTRY_NAME>.azurecr.io`

1. Open **CameraTaggingModule/module.json** and change the version setting in the tag property to create a new version of the module image.

1. Set the environment variables found in deployment.template.json

1. Right-click on deployment.template.json and select the **Build and Push IoT Edge Solution** command to generate a new deployment.json file in the config folder, build a module image, and push the image to the specified ACR repository.
    > Note: Some red warnings "Unknown host QEMU_IFLA type: ##" and "qemu: Unsupported syscall: ##" displayed during the building process can be ignored.

1. Right-click on config/deployment.json, select **Create Deployment for Single Device**, and choose the targeted IoT Edge device to deploy the container image.

1. You'll find troubleshooting steps at <https://visionaidevkitsupport.azurewebsites.net/>.

### Setting Environment Variables

Open deployment.template.json and find **env** under **CameraTaggingModule**.

- You can update the following environment variables here:

    | Variable Name                        | Description                                 | Default Value  |  
    | ------------------------------------ | ------------------------------------------- | :------------: |  
    | RTSP_IP                              | IP address for the rtsp stream              | None           |  
    | RTSP_PORT                            | Port for the rtsp stream                    | 554            |  
    | RTSP_PATH                            | Path for the rtsp stream                    | ''             |  
    | REACT_APP_LOCAL_STORAGE_MODULE_NAME  | Module name of local storage                | None           |  
    | REACT_APP_LOCAL_STORAGE_PORT         | Local storage port                          | None           |  
    | REACT_APP_LOCAL_STORAGE_ACCOUNT_NAME | Local storage account name                  | None           |  
    | REACT_APP_LOCAL_STORAGE_ACCOUNT_KEY  | Local storage account key                   | None           |  
    | REACT_APP_SERVER_PORT                | Port by which client and server communicate | 3003           |  
    | REACT_APP_WEB_SOCKET_PORT            | Port by which client receives video stream  | 3002           |  

- If you do not wish to set the RTSP environment variables, you can enter them from the web page itself.
- If you do not wish to set up the Local Storage environment variables, you will have the option to push images directly to blob storage in the cloud.
  - Alternatively, you can push to local storage from the *Push to Blob Store* web page by constructing a connection string to your local blob storage and inputting the name of your local storage container under the field *Container Name*.
  - Local Blob Store Connection String: `DefaultEndpointsProtocol=http;BlobEndpoint=http://<local_storage_module_name>:<local_storage_port>/<local_storage_account_name>;AccountName=<local_storage_account_name>;AccountKey=<local_storage_account_key>`
- If you do not wish to set the port environment variables, they will default to the following:
  - REACT_APP_SERVER_PORT: 3003
  - REACT_APP_WEB_SOCKET_PORT: 3002
  > Note: Make sure to appropriately bind the REACT_APP_SERVER_PORT and REACT_APP_WEB_SOCKET_PORT under the **PortBindings** section.

## Access the Webpage

Find the IP address of the IoT Edge device:

- At the end of [Vision AI Developer Kit set up](https://azure.github.io/Vision-AI-DevKit-Pages/docs/Get_Started/#), the IP address is shown.
- Using a serial or network connection open a shell window to the device and type `ifconfig wlan0` to see the wireless IP address.

> Note: your workstation needs to be on the same WLAN as the device to access it.

Open a browser to http://DEVICE_IP:3000 where DEVICE_IP is the IP address you found above.

## Direct Methods

### Capture

- Method Name: capture
- Payload:
    {  
        "RTSP_IP":"<rtsp_ip>",  
        "RTSP_PORT":"<rtsp_port>",  
        "RTSP_PATH":"<rtsp_path>",  
        "TAGS":"[<tags>]"  
    }  
    
    | Variable Name  | Required  | Default Value  |
    |----------------|:---------:|:--------------:|
    | RTSP_IP        | True      | None           |
    | RTSP_PORT      | False     | 554            |
    | RTSP_PATH      | False     | ''             |
    | TAGS           | True      | None           |

### Push to Local Blob Storage

- Method Name: push
- Payload:
    {  
        "MODULE_NAME":"<module_name>",  
        "STORAGE_PORT":"<storage_port>",  
        "ACCOUNT_NAME":"<account_name>",  
        "DELETE":"true"  
    }  
    
    | Variable Name  | Required  | Description                                           |
    |----------------|:---------:|-------------------------------------------------------|
    | MODULE_NAME    | True      | Azure IoT Local Storage Module name                   |
    | STORAGE_PORT   | True      | Port the local storage module operates through        |
    | ACCOUNT_NAME   | True      | Name of the local storage account                     |
    | ACCOUNT_KEY    | True      | Local storage account key                             |
    | DELETE         | False     | Optional flag that will delete all images once pushed |

### Delete All Images

- Method Name: delete
- Payload: {}

## Azure-Blob-Storage Module

Refer to [Deploy Blob Storage Modules](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-deploy-blob#deploy-from-visual-studio-code) to configure the settings of your local storage.

## Troubleshooting

- Browser
  - Open developer tools in your browser, and view the Console to look for any client-side errors.
  - If the stream fails to load, check the RTSP stream by using a media player (e.g. VLC).
- Server
  - Once deployed, check the logs `iotedge logs CameraTaggingModule` to view traces from the website. The edgeAgent and edgeHub modules may also have relevant output to check.
  - If the ffmpeg process failed to start, refresh the webpage and it will restart ffmpeg.
    > Note: this means that if no clients are viewing the stream, ffmpeg will not run and therefore not consume any CPU cycles.
- The module requires ports 3000-3003 to be used by the website. If those ports are in use by other software, there could be a conflict.
