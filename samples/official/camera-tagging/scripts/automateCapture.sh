#!/bin/bash

while true; do
        ./capture.sh 'username:password@rtsp_ip' rtsp_port rtsp_path
        sleep 15
        ./capture.sh 'username:password@rtsp_ip' rtsp_port rtsp_path
        sleep 15
        ./capture.sh 'username:password@rtsp_ip' rtsp_port rtsp_path
        sleep 15
        ./capture.sh 'username:password@rtsp_ip' rtsp_port rtsp_path
        sleep 15
        ./push.sh
done