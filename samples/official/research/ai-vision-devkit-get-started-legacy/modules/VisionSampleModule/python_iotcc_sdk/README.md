# Introduction
This package provides QTI's python SDK for developing IOT connected camera applications. The SDK provide simplified python APIs on top
of QTI's IP Camera webserver (IPC-webserver). QTI's IPC-webserver is reference application which provides RESTful APIs for web based access to QTI's multimedia framework (QMMF) SDK. QMMF SDK encapsulates common connected camera features and provides an easy to use API to simplify application development across various connected camera application.

Below is the list of currently supported APIs with a brief description of their functionality.
* connect: connect to the camera
* captureimage: capture an image
* configure_preview: configure preview parameters
* configure_overlay: configure overlay parameters
* get_inferences: get inferences from the analytics metadata stream
* logout: logout from the camera
* set_overlay_state: switch overlay on/off
* set_preview_state: switch preview on/off
* set_recording_state: switch recording on/off
* set_analytics_state: switch video analytics on/off

The detailed description and the expected parameters can be found in the documentation.

# Pre-requisites
## Install Python version 3.5
Install python version **_3.5_** as per your operating system
https://www.python.org/downloads/

**_Make sure the installed bin path is set in your PATH variable. Run "python --version" on command prompt to check_**

NOTE: This SDK is tested with python version 3.5 only. Other versions may not work.

## Install gstreamer (v1.14.x or higher)
### Windows
1. Download the latest package from

https://gstreamer.freedesktop.org/data/pkg/windows/

```
gstreamer-1.0-x86* (per your architecture)
```

**_Make sure the installed bin path is set in your PATH variable. Run "gst-inspect-1.0 --version" on command prompt to check_**

### Linux
```
apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools
```
Note: you may have to use ```sudo``` with the above command if you don't have permission to install packages.

# Build and install
```
cd python_iotcc_sdk
pip install -e .
```
If you are updating to new version of sdk
```
cd python_iotcc_sdk
pip install --user --force-reinstall .
```
#Test
## Quick test (**no network connectivity required**)
* Connect device via USB
* Connect display via HDMI
* Reset the device and setup port forwarding
  * Windows
    ```
    tests\port_forward.bat
    ```
  * Linux
    ```
    tests\port_forward.sh
    ```

* Run the test script from your machine

    ```
    python test-preview.py --ip 127.0.0.1
    ```
    Use --help or -h for all options. And press Ctrl-C for exiting.
You can see preview on display via HDMI.

## Quick test (**with network connectivity**)
* Connect the device to network (WiFi)
* Check camera ip
* Connect display via HDMI
* Run the test script from your machine

    ```
    python test-preview.py --ip <ip address>
    ```
    Use --help or -h for all options. And press Ctrl-C for exiting.
You can see preview on display via HDMI.

## Other tests
Below test available in tests folder are verified with this SDK.
* ```test-preview.py```: Illustrates configuring and starting preview with HDMI out.
* ```test-preview-record.py```: Illustrates recording along with preview use case.
* ```test-preview-snapshot.py```: Illustrates snapshot along with preview use case.
* ```test-preview-inference-overlay.py```: Illustrates HDMI preview with overlay based on video analytics inferences

    **NOTE: This test case requires ML model and SNPE engine on target device**
* ```test-preview-inference-overlay-snapshot.py```: Illustrates HDMI preview with overlay based on video analytics inferences and takes a        snapshot when the object detected has confidence value more 90%

    **NOTE: This test case requires ML model and SNPE engine on target device**


# References
1. https://gstreamer.freedesktop.org/documentation/installing/on-windows.html
2. https://gstreamer.freedesktop.org/documentation/installing/on-linux.html
