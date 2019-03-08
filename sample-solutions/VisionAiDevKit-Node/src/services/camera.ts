// Copyright (c) 2018, The Linux Foundation. All rights reserved.
// Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
// full license information.

// This module contains the high level client APIs.

import IpcProvider from './ipcProvider';
import { VideoInferenceIterator } from './frameIterators';
import { logger } from './logger';

export default class CameraClient {
    public static connect(username: string, password: string, ipAddress: string): CameraClient {
        const connection = new IpcProvider(username, password, ipAddress);

        try {
            connection.connect();
            return new CameraClient(connection);
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            throw new Error(ex.message);
        }
    }

    private connection: IpcProvider = null;
    private previewRunning: boolean = false;
    private previewUrl: string = '';
    private vamRunning: boolean = false;
    private vamUrl: string = '';
    private resolutions: any[] = [];
    private encodetype: any[] = [];
    private bitrates: any[] = [];
    private framerates: any[] = [];

    constructor(connection: IpcProvider) {
        this.connection = connection;
        this.previewRunning = false;
        this.previewUrl = '';
        this.vamRunning = false;
        this.vamUrl = '';
        this.resolutions = [];
        this.encodetype = [];
        this.bitrates = [];
        this.framerates = [];
    }

    // Inference generator for the application.
    //
    // This inference generator gives inferences from the VA metadata stream.
    //
    // Parameters
    // ----------
    // inferenceIterator : VideoInferenceIterator class object
    //
    // Yields
    // ------
    // AiCameraInference: AiCameraInference class object
    //     This AiCameraInference object yielded
    //     from VideoInferenceIterator.start()
    //
    // Raises
    // ------
    // EOFError
    //     If the preview is not started.
    //     Or if the vam is not started.

    public * getInferences(inferenceIterator: any) {
        if (!this.previewRunning) {
            throw new Error('preview not started');
        }

        if (!this.vamRunning) {
            throw new Error('VAM not started');
        }

        if (!inferenceIterator) {
            inferenceIterator = new VideoInferenceIterator();
        }

        try {
            if (!this.vamUrl) {
                this.getVamInfo();
            }

            if (this.vamUrl.indexOf('0.0.0.0') !== -1) {
                this.vamUrl = this.vamUrl.replace('0.0.0.0', '127.0.0.1');
            }

            yield inferenceIterator.start(this.vamUrl);
        }
        finally {
            inferenceIterator.stop();
        }
    }

    // This method is for setting preview params.
    //
    // Parameters
    // ----------
    // resolution : str
    //     A value from resolutions attribute
    // encode : str
    //     A value from encodetype attribute
    // bitrate : str
    //     A value from bitrates attribute
    // framerate : int
    //     A value from framerates attribute
    // display_out : {0, 1}
    //     For enabling or disabling HDMI output
    //
    // Returns
    // -------
    // bool
    //     True if the request is successful. False on failure.

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
            const response = await this.connection.post('/video', payload);

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    // This is a switch for preview.
    //
    // Preview can be enabled or disabled using this API.
    //
    // Parameters
    // ----------
    // status : bool
    //     Set it True for enabling and False for disabling preview.
    //
    // Returns
    // -------
    // bool
    //     True if the request was successful. False on failure.

    public async togglePreview(status) {
        const payload = {
            switchStatus: status
        };

        try {
            const response = await this.connection.post('/preview', payload);

            this.previewRunning = response.status;

            return this.previewRunning;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    // This is a switch for VA.

    // VA can be enabled or disabled using this API.

    // Parameters
    // ----------
    // status : bool
    //     Set it True for enabling and False for disabling VA.

    // Returns
    // -------
    // bool
    //     True if the request was successful. False on failure.

    public async toggleVam(status) {
        const payload = {
            switchStatus: status,
            vamconfig: 'MD'
        };

        try {
            const response = await this.connection.post('/vam', payload);

            this.vamRunning = response.status;

            return this.vamRunning;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    // This is for configuring overlay params.
    //
    // Parameters
    // ----------
    // type : {None, "inference", "text"}
    //     Type of the overlay you want to configure.
    // text : str, optional
    //     Text for text overlay type (the default is None).
    //
    // Returns
    //     True if the configuration was successful.
    //     False on failure.

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

    // This is a switch for overlay.
    //
    // Overlay can be enabled or disabled using this API.
    //
    // Parameters
    // ----------
    // status : bool
    //     Set it True for enabling and False for disabling overlay.
    //
    // Returns
    // -------
    // bool
    //     True if the request was successful. False on failure.

    public async toggleOverlay(status) {
        const payload = {
            switchStatus: status
        };

        try {
            const response = await this.connection.post('/overlay', payload);

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    // This method is for logging out from the camera.
    //
    // Returns
    // -------
    // bool
    //     True if the request was successful. False on failure.

    public async logout() {
        try {
            const response = await this.connection.post('logout', {});

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    // Private method for inference overlay configuration.
    //
    // This is used by configure_overlay for inference type overlay.
    //
    // Returns
    // -------
    // bool
    //     True if the configuration was successful.
    //     False on failure.

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
            const response = await this.connection.post('/overlayconfig', payload);

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    // Private method for text overlay configuration.
    //
    // This is used by configure_overlay for text type overlay.
    //
    // Returns
    // -------
    // bool
    //     True if the configuration was successful.
    //     False on failure.

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
            const response = await this.connection.post('overlayconfig', payload);

            return response.status;
        }
        catch (ex) {
            logger.log(['cameraClient', 'error'], ex.message);

            return false;
        }
    }

    // Private method for getting VA url
    //
    // Returns
    // -------
    // str
    //     Preview VA url

    private async getVamInfo() {
        try {
            const response = await this.connection.get('/vam');

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

    // Private method for getting preview url
    //
    // Returns
    // -------
    // str
    //     Preview RTSP url

    private async getPreviewInfo() {
        try {
            const response = await this.connection.get('/preview');

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

    // Private method for getting preview params
    //
    // This method populates the resolutions, encodetype, bitrates
    // and framerates attribute. It is called by configure preview.
    //
    // Returns
    // -------
    // bool
    //     True if the request is successful. False on failure.

    private async getCameraParams() {
        const path = '/video';

        try {
            const response = await this.connection.get('/video');

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

    private setupModel(modelConfig) {
        return;
    }
}
