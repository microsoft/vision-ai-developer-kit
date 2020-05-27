#!/bin/bash

#Configuration
iothubName=iothubName
deviceId=deviceId
#Generated with 'az iot hub generate-sas-token -n <iothubName> -du 31536000'
SharedAccessSignature='SharedAccessSignature sr=iothubname.azure-devices.net&sig=x&se=x&skn=iothubowner'

curl -X POST \
  https://$iothubName.azure-devices.net/twins/$deviceId/modules/CameraTaggingModule/methods?api-version=2018-06-30 \
  -H "Authorization: $SharedAccessSignature" \
  -H 'Content-Type: application/json' \
  -d '{
    "methodName": "push",
    "responseTimeoutInSeconds": 200,
    "payload": {
        "MODULE_NAME":"azureblobstorageoniotedge",
        "STORAGE_PORT":"11002",
        "ACCOUNT_NAME":"camerataggingmodulelocal",
        "ACCOUNT_KEY":"jukoPNlrFwXR/eELSxryaw==",
        "DELETE":"true"
    }
  }'