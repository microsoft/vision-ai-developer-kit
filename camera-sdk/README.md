
## Python SDK for AI Vision Developer Kit

This library allows developer to control the [Qualcomm Visual Intelligence Platform](https://www.qualcomm.com/news/onq/2018/05/07/qualcomm-vision-intelligence-platform-microsoft-azure-bring-edge-ai-solution) for hardware acceleration fo AI models to deliver superior inferencing performance.

The library enables developers to easily combine the Vision AI DevKit with [Azure IoT Edge](https://azure.microsoft.com/en-us/services/iot-edge/) to deploy vision ML models and custom business logic from the cloud to the edge.  

## Usage

The main class for controlling the camera is the CameraClient:

```python
from iotccsdk import CameraClient
camera_client = CameraClient.connect(username="admin", password="admin", ip_address=<camera ip address>)
camera_client.configure_preview(resolution="1080P",encode="AVC/H.264",bitrate="1.5Mbps",display_out=1)
camera_client.set_preview_state("on")
rtsp_stream_address = camera_client.preview_url
```

For more complete code examples see the samples folder in the project GitHub repository https://github.com/microsoft/vision-ai-developer-kit.

## Release History


0.1.4 (2019-06-19)

* Update project metadata and readme

0.1.0 (2019-06-19)

* Project creation

