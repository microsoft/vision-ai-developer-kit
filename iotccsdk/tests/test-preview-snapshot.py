# Copyright (c) 2019, The Linux Foundation. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#    * Neither the name of The Linux Foundation nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import sys
import time
import subprocess

sys.path.append('../iotccsdk')
from iotccsdk.camera import CameraClient

def main(protocol=None):
    print("\nPython %s\n" % sys.version)
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', help='ip address of the camera', default='127.0.0.1')
    parser.add_argument('--username', help='username of the camera', default='admin')
    parser.add_argument('--password', help='password of the camera', default='admin')
    args = parser.parse_args()
    ip_addr = args.ip
    username = args.username
    password = args.password

    with CameraClient.connect(ip_address=ip_addr, username=username, password=password) as camera_client:
        print('supported resolutions: ' + str(camera_client.resolutions))
        print('supported encodetype: ' + str(camera_client.encodetype))
        print('supported bitrates: ' + str(camera_client.bitrates))
        print('supported framerates: ' + str(camera_client.framerates))
        print(camera_client.configure_preview(resolution="1080P", display_out=1))

        camera_client.set_preview_state("on")

        print("Running for 30 seconds")
        time.sleep(30)
        print("Taking snapshot")
        if not camera_client.captureimage():
            print("captureimage failed")
        print("Running for 30 seconds")
        time.sleep(30)

        camera_client.set_preview_state("off")
        camera_client.logout()


if __name__ == '__main__':
    main()
