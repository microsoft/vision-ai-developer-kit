// Copyright (c) 2018, The Linux Foundation. All rights reserved.
// Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
// full license information.

// This module contains the high level client APIs.

import { EventEmitter } from 'events';
import { IpcProvider } from './ipcProvider';
import { InferenceStreamProcessor, FrameInference, FrameInferenceObject } from './inferenceStream';
import { logger } from '../services/logger';

export class CameraClient extends EventEmitter {
    public static async connect(username: string, password: string, ipAddress: string): Promise<CameraClient> {
        const ipcSession = IpcProvider.getInstance(username, password, ipAddress);

        try {
            await ipcSession.ipcLogin();

            const cameraClient = new CameraClient(ipcSession);

            return cameraClient;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            ipcSession.ipcLogout();

            throw new Error(ex.message);
        }
    }

    private ipcSession: any = null;
    private previewRunning: boolean = false;
    private previewUrl: string = '';
    private vamRunning: boolean = false;
    private vamUrl: string = '';
    private resolutions: any[] = [];
    private encodetype: any[] = [];
    private bitrates: any[] = [];
    private framerates: any[] = [];

    constructor(ipcSession: IpcProvider) {
        super();

        this.ipcSession = ipcSession;
        this.previewRunning = false;
        this.previewUrl = '';
        this.vamRunning = false;
        this.vamUrl = '';
        this.resolutions = [];
        this.encodetype = [];
        this.bitrates = [];
        this.framerates = [];
    }

    public async getInferences(inferenceProcessor?: InferenceStreamProcessor) {
        this.previewRunning = true;
        this.vamRunning = true;
        if (!this.previewRunning) {
            throw new Error('preview not started');
        }

        if (!this.vamRunning) {
            throw new Error('VAM not started');
        }

        if (!inferenceProcessor) {
            inferenceProcessor = new InferenceStreamProcessor();
        }

        try {
            if (!this.vamUrl) {
                this.getVamInfo();
            }

            if (this.vamUrl.indexOf('0.0.0.0') !== -1) {
                this.vamUrl = this.vamUrl.replace('0.0.0.0', '127.0.0.1');
            }

            inferenceProcessor.on('inference', async (inference: FrameInference) => {
                const scaledInference = this.scaleInference(inference);

                if (this.listenerCount('inference') > 0) {
                    this.emit('inference', scaledInference);
                }
            });

            inferenceProcessor.start(this.vamUrl);
        }
        finally {
            inferenceProcessor.stop();
        }
    }

    public async configurePreview(resolution: any, encode: any, bitrate: any, framerate: any, displayOut: any) {
        let res = 1; // 1080P
        if (resolution && this.resolutions) {
            res = this.resolutions.indexOf(item => item === resolution);
            if (res === -1) {
                res = 1;
            }
        }

        let enc = 0; // HEVC
        if (encode && this.encodetype) {
            enc = this.encodetype.indexOf(item => item === encode);
            if (enc === -1) {
                enc = 0;
            }
        }

        let bit = 6; // 4Mbps
        if (bitrate && this.bitrates) {
            bit = this.bitrates.indexOf(item => item === bitrate);
            if (bit === -1) {
                bit = 6;
            }
        }

        let fps = 1; // 30
        if (framerate && this.framerates) {
            fps = this.framerates.indexOf(item => item === framerate);
            if (fps === -1) {
                fps = 1;
            }
        }

        displayOut = 0;
        if (displayOut < 0 && displayOut > 1) {
            logger.log(['cameraClient', 'info'], `Invalid value: displayOut should be 0 or 1, default=0`);
        }

        const payload = {
            resolutionSelectVal: res,
            encodeModeSelectVal: enc,
            bitRateSelectVal: bit,
            fpsSelectVal: fps,
            displayOut
        };

        try {
            const response = await this.ipcSession.ipcPostRequest('/video', payload);

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    public async togglePreview(status) {
        const payload = {
            switchStatus: status
        };

        try {
            const response = await this.ipcSession.ipcPostRequest('/preview', payload);

            return this.previewRunning = response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    public async toggleVam(status) {
        const payload = {
            switchStatus: status,
            vamconfig: 'MD'
        };

        try {
            const response = await this.ipcSession.ipcPostRequest('/vam', payload);

            return this.vamRunning = response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    public configureOverlay(type: any, text: string) {
        if (type === 'inference') {
            return this.configureInferenceOverlay();
        }
        else if (type === 'text') {
            return this.configureTextOverlay(text);
        }

        logger.log(['cameraClient', 'error'], 'Invalid overlay type use (inference/text)');
        return false;
    }

    public async toggleOverlay(status) {
        const payload = {
            switchStatus: status
        };

        try {
            const response = await this.ipcSession.ipcPostRequest('/overlay', payload);

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    public async logout() {
        try {
            const response = await this.ipcSession.ipcPostRequest('logout');

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    private async configureInferenceOverlay() {
        const payload = {
            ov_type_SelectVal: 5,
            ov_position_SelectVal: 0,
            ov_color: '869007615',
            ov_usertext: 'Text',
            ov_start_x: 0,
            ov_start_y: 0,
            ov_width: 0,
            ov_height: 0
        };

        try {
            const response = await this.ipcSession.ipcPostRequest('/overlayconfig', payload);

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    private async configureTextOverlay(text: string) {
        const payload = {
            ov_type_SelectVal: 0,
            ov_position_SelectVal: 0,
            ov_color: '869007615',
            ov_usertext: text,
            ov_start_x: 0,
            ov_start_y: 0,
            ov_width: 0,
            ov_height: 0
        };

        try {
            const response = await this.ipcSession.ipcPostRequest('overlayconfig', payload);

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    private async getVamInfo() {
        try {
            const response = await this.ipcSession.ipcGetRequest('/vam');

            if (this.vamRunning) {
                this.vamUrl = response.url;
            }

            return this.vamUrl;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    private async getPreviewInfo() {
        try {
            const response = await this.ipcSession.ipcGetRequest('/preview');

            if (this.previewRunning) {
                this.previewUrl = response.url;
            }

            return this.previewUrl;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    private async getCameraParams() {
        const path = '/video';

        try {
            const response = await this.ipcSession.ipcGetRequest('/video');

            if (response.status) {
                this.resolutions = response.resolution;
                this.encodetype = response.encodeMode;
                this.bitrates = response.bitRate;
                this.framerates = response.fps;
            }

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    private scaleInference(inference) {
        if (!inference) {
            return;
        }

        const objects = inference.objects;
        if (objects && Array.isArray(objects)) {
            const scaledObjects = objects.map((object: FrameInferenceObject) => {
                return {
                    ...object,
                    position: {
                        x: (object.position.x * 1920) / 10000,
                        y: (object.position.y * 1080) / 10000,
                        width: (object.position.width * 1920) / 10000,
                        height: (object.position.height * 1080) / 10000
                    }
                };
            });

            return {
                timestamp: inference.timestamp,
                objects: scaledObjects
            };
        }
        else {
            return {
                timestamp: inference.timestamp || Date.now(),
                objects: []
            };
        }
    }

    private setupModel(modelConfig) {
        return;
    }
}
