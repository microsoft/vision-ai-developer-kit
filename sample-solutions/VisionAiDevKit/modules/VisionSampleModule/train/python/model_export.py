import http.client, urllib.request, urllib.parse, urllib.error
import __init__

module_name = "visionsample"
# Resource group in Azure
resource_group_name= ws.resource_group
iot_rg="vaidk_"+resource_group_name

try:
    conn = http.client.HTTPSConnection(__init__.ENDPOINT)
    conn.request("GET", "/customvision/v2.2/Training/projects/{projectId}/iterations/{iterationId}/export?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))


########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64

headers = {
    # Request headers
    'Training-Key': 'c4b7dd17c68a48629f041516e25faf22',
    'Training-key': '{c4b7dd17c68a48629f041516e25faf22}',
}

params = urllib.parse.urlencode({
})

try:
    conn = http.client.HTTPSConnection('southcentralus.api.cognitive.microsoft.com')
    conn.request("GET", "/customvision/v2.2/Training/projects/{projectId}/iterations/{iterationId}/export?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
    model_file = open("../models/plant.export", "w")
    model_file.write(data)
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

####################################
