# Copyright (c) 2018, The Linux Foundation. All rights reserved.
# Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
# full license information.

class ModelInferenceConfig(object):
    def __init__(self, height=None, width=None,
                 pixel_norm=None, mean_subtract=None,
                 confidence_threshold=None,
                 model_path=None, label_path=None,
                 input_nodes=None, output_nodes=None):

        self.height = height
        self.width = width
        self.pixel_norm = pixel_norm
        self.mean_subtract = mean_subtract
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        self.label_path = label_path
        self.input_nodes = input_nodes
        self.output_nodes = output_nodes

def get_mobilenet_ssd_config(model_path, label_path, confidence_threshold=0):
    return ModelInferenceConfig(
        height=224, width=224,
        pixel_norm=128, mean_subtract=[123,117,104],
        confidence_threshold=confidence_threshold,
        model_path=model_path, label_path=label_path,
        input_nodes="input",
        output_nodes=["prob"]
    )
