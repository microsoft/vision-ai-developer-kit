REM Copyright (c) 2018-2019, The Linux Foundation. All rights reserved.
REM
REM Redistribution and use in source and binary forms, with or without
REM modification, are permitted provided that the following conditions are
REM met:
REM    * Redistributions of source code must retain the above copyright
REM      notice, this list of conditions and the following disclaimer.
REM    * Redistributions in binary form must reproduce the above
REM      copyright notice, this list of conditions and the following
REM      disclaimer in the documentation and/or other materials provided
REM      with the distribution.
REM    * Neither the name of The Linux Foundation nor the names of its
REM      contributors may be used to endorse or promote products derived
REM      from this software without specific prior written permission.
REM
REM THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
REM WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
REM MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
REM ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
REM BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
REM CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
REM SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
REM BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
REM WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
REM OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
REM IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

adb reboot
adb wait-for-device root
adb shell mount -o remount,rw /

adb forward tcp:8900 tcp:8900
adb forward tcp:8901 tcp:8901
adb forward tcp:8902 tcp:8902

adb forward tcp:1080 tcp:1080

adb forward tcp:4000 tcp:4000

adb shell ps -a | grep server