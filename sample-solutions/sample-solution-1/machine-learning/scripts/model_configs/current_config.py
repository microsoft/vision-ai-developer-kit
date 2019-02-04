# ==============================================================================
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.
# ==============================================================================

from easydict import EasyDict as edict

__BASE = edict()
cfg = __BASE

# Settings used in Model.register()
__BASE.MODEL_PATH = "MachineLearning/models/mobilenet-imagenet/orig/"
__BASE.MODEL_NAME = "imagenet_2_frozen.pb"
__BASE.MODEL_TAGS = {'Device': "peabody", 'type': "mobilenet", 'area': "iot", 'version': "1.0"}
__BASE.MODEL_DESCRIPTION = "TF SNPE quantization friendly MobileNet"

# Settings used in SnpeConverter.convert_tf_model()
__BASE.MODEL_INPUT_NODE = "input"
__BASE.MODEL_INPUT_DIMS = "1,224,224,3"
__BASE.MODEL_OUTPUTS_NODES = ["MobilenetV1/Predictions/Reshape_1"]

# Settings used in Image.create())
__BASE.IMAGE_NAME = "mobilenetimagenet"

# Settings used in IotContainerImage.image_configuration()
__BASE.IMAGE_TAGS = ["mobilenet"]
__BASE.IMAGE_DESCRIPTION = "Updated MobileNet trained on ImageNet"

# Settings used in
__BASE.MODULE_NAME = "VisionSampleImagenet"