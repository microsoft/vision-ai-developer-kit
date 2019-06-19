# ==============================================================================
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.
# ==============================================================================

from easydict import EasyDict as edict

__BASE = edict()
cfg = __BASE

# Settings used in Model.register()
__BASE.MODEL_PATH = "MachineLearning/models/mobilenet-retrain-cloud/outputs/"
__BASE.MODEL_NAME = "retrained_graph.pb"
__BASE.MODEL_TAGS = {"Device": "peabody", "type": "mobilenet", "area": "iot", "version": "1.0"}
__BASE.MODEL_DESCRIPTION = "Retrained MobileNet model by soda_cans dataset"

# Settings used in SnpeConverter.convert_tf_model()
__BASE.MODEL_INPUT_NODE = "input"
__BASE.MODEL_INPUT_DIMS = "1,224,224,3"
__BASE.MODEL_OUTPUTS_NODES = ["final_result"]

# Settings used in Image.create())
__BASE.IMAGE_NAME = "mobilenetretraincloud"

# Settings used in IotContainerImage.image_configuration()
__BASE.IMAGE_TAGS = ["mobilenet"]
__BASE.IMAGE_DESCRIPTION = "Retrained MobileNet model by soda_cans dataset"

# Settings used in deployment.json
__BASE.MODULE_NAME = "VisionSampleImagenet_retrain_cloud"

# Settings used in SnpeConverter API (TensorFlow / Caffe)
__BASE.SNPECONVERTER_TYPE = "TensorFlow"