# ==============================================================================
# Copyright (c) Microsoft. All rights reserved.
#
# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

from easydict import EasyDict as edict

__BASE = edict()
cfg = __BASE

# Settings used in Model.register()
__BASE.MODEL_PATH = "MachineLearning/models/caffe_v2_fork_scissors/"
__BASE.MODEL_NAME = "model.caffemodel"
__BASE.MODEL_TAGS = {"Device": "peabody", "type": "caffe", "area": "iot", "version": "1.0"}
__BASE.MODEL_DESCRIPTION = "Caffe V2 model by fork scissors dataset"

# Settings used in SnpeConverter.convert_tf_model()
__BASE.MODEL_INPUT_NODE = ""
__BASE.MODEL_INPUT_DIMS = ""
__BASE.MODEL_OUTPUTS_NODES = []

# Settings used in Image.create())
__BASE.IMAGE_NAME = "caffev2forkscissors"

# Settings used in IotContainerImage.image_configuration()
__BASE.IMAGE_TAGS = ["caffe"]
__BASE.IMAGE_DESCRIPTION = "Caffe V2 model by fork scissors dataset"

# Settings used in
__BASE.MODULE_NAME = "VisionSampleCaffe_V2"

# Settings used in SnpeConverter API (TensorFlow / Caffe)
__BASE.SNPECONVERTER_TYPE = "Caffe"