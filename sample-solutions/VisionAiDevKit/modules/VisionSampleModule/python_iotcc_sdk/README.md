# Introduction 
This respository has code for the Python SDK and examples.

# Pre-requisites
## Install Python version 3.x
Install python version **_3.x_** as per your operating system
https://www.python.org/downloads/

## Install gtreamer (v1.14.x or higher)
### Windows
1. Download the latest package from 
   https://gstreamer.freedesktop.org/data/pkg/windows/
``` 
gstreamer-1.0-x86* (per your architecture)
```

**_Make sure the installed bin path is set in your PATH variable._**

### Linux
```
apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools
```
Note: you may have to use ```sudo``` with the above command if you don't have permission to install packages.

# Build and Test
## Install the SDK package
```
cd python_iotcc_sdk
pip install -e .
```
## Reset the device
# inits the device and sets up port forwarding
## Windows
```
tests\init.bat
```
## Linux
```
tests\init.sh
```
## Run the test script from your machine

```
python test-main.py
```
Use --help or -h for all options.

# References
1. https://gstreamer.freedesktop.org/documentation/installing/on-windows.html
2. https://gstreamer.freedesktop.org/documentation/installing/on-linux.html 