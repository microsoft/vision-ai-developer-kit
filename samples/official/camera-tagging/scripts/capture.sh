#!/bin/bash

#Configuration
iothubName=iothubname
deviceId=deviceId
#Generated with 'az iot hub generate-sas-token -n <iothubName> -du 31536000'
SharedAccessSignature='SharedAccessSignature sr=iothubname.azure-devices.net&sig=x&se=x&skn=iothubowner'

usage(){
  echo "***Camera Tagging Module Capture Script***"
  echo "Usage: ./capture.sh <rtsp_ip> <rtsp_port> <rtsp_path>"
}

capture(){
curl -X POST \
  https://$iothubName.azure-devices.net/twins/$deviceId/modules/CameraTaggingModule/methods?api-version=2018-06-30 \
  -H "Authorization: $SharedAccessSignature" \
  -H 'Content-Type: application/json' \
  -d "{
    \"methodName\": \"capture\",
    \"responseTimeoutInSeconds\": 200,
    \"payload\": {
        \"RTSP_IP\":\"$rtsp_ip\",
        \"RTSP_PORT\":\"$rtsp_port\",
        \"RTSP_PATH\":\"$rtsp_path\",
        \"TAGS\":[\"automatedCaptures\"]
    }
  }"
}


# Arguments
rtsp_ip=$1
rtsp_port=$2
rtsp_path=$3

# Check Arguments
[ "$#" -ne 3 ] && { usage && exit 1; } || capture