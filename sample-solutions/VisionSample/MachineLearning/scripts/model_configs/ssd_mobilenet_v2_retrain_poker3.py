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
__BASE.MODEL_PATH = "MachineLearning/models/ssd_mobilenet_v2_retrain_poker3/"
__BASE.MODEL_NAME = "frozen_inference_graph.pb"
__BASE.MODEL_TAGS = {"Device": "peabody", "type": "mobilenetssd", "area": "iot", "version": "1.0"}
__BASE.MODEL_DESCRIPTION = "MobileNet V2 SSD retrain with poker3 dataset"

# Settings used in SnpeConverter.convert_tf_model()
__BASE.MODEL_INPUT_NODE = "Preprocessor/sub"
__BASE.MODEL_INPUT_DIMS = "1,300,300,3"
__BASE.MODEL_OUTPUTS_NODES = ["detection_classes", "detection_boxes", "detection_scores"]

# Settings used in Image.create())
__BASE.IMAGE_NAME = "mobilenetssdv2poker3"

# Settings used in IotContainerImage.image_configuration()
__BASE.IMAGE_TAGS = ["mobilenetssd"]
__BASE.IMAGE_DESCRIPTION = "MobileNet V2 SSD retrain with poker3 dataset"

# Settings used in
__BASE.MODULE_NAME = "VisionSampleSSD_V2_retrain"

# Settings used in deployment.json
__BASE.MODULE_NAME = "VisionSampleImagenetSSD_V2_Poker3"

# Settings used in SnpeConverter API (TensorFlow / Caffe)
__BASE.SNPECONVERTER_TYPE = "TensorFlow"