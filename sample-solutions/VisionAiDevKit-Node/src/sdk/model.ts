// Copyright (c) 2018, The Linux Foundation. All rights reserved.
// Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
// full license information.

export default class ModelInferenceConfig {
    // @ts-ignore
    private height: number;
    // @ts-ignore
    private width: number;
    // @ts-ignore
    private pixelNorm: any;
    // @ts-ignore
    private meanSubtract: any;
    // @ts-ignore
    private confidenceThreshold: number;
    // @ts-ignore
    private modelPath: string;
    // @ts-ignore
    private labelPath: string;
    // @ts-ignore
    private inputNodes: any;
    // @ts-ignore
    private outputNodes: any;

    constructor(height: number, width: number, pixelNorm: any, meanSubtract: any,
                confidenceThreshold: number, modelPath: string, labelPath: string, inputNodes: any, outputNodes: any) {
        this.height = height;
        this.width = width;
        this.pixelNorm = pixelNorm;
        this.meanSubtract = meanSubtract;
        this.confidenceThreshold = confidenceThreshold;
        this.modelPath = modelPath;
        this.labelPath = labelPath;
        this.inputNodes = inputNodes;
        this.outputNodes = outputNodes;
    }

    public get_mobilenet_ssd_config(modelPath: string, labelPath: string, confidenceThreshold: number = 0) {
        return new ModelInferenceConfig(224, 224, 128, [123, 117, 104], confidenceThreshold, modelPath, labelPath, 'input', ['prob']);
    }
}
