import { spawn } from 'child_process';
import { config } from './config';
import { logger } from './logger';
import { objectDetector } from './objectDetector';
import PicProcessor from './picProcessor';

class ControllerService {
    private gotOne = 0;

    public async run(context: any) {
        logger.log(['controller', 'info'], `Starting capture processes`);

        try {
            const appContext = {
                ...context,
                ...{
                    useWebCam: config.get('useWebCam'),
                    webCamDeviceIndex: config.get('webCamDeviceIndex')
                }
            };

            await objectDetector.init(appContext);

            if (!appContext.useWebCam) {
                const ffmpegProcess = spawn(config.get('ffmpegCommand'),
                    config.get('captureCommandArgs').split(' '),
                    { stdio: ['ignore', 'pipe', 'ignore'] });

                ffmpegProcess.on('error', (error) => {
                    logger.log(['ControllerService', 'error'], `ffmpegProcess.on(error): ${error}`);
                });

                ffmpegProcess.on('exit', (code, signal) => {
                    logger.log(['ControllerService', 'info'], `ffmpegProcess.on(exit), code: ${code}, signal: ${signal}`);
                });

                const picProcessor = new PicProcessor({});

                // @ts-ignore (jpeg)
                picProcessor.on('jpeg', async(jpeg: Buffer) => {
                    if (!this.gotOne) {
                        this.gotOne = 0;
                        await objectDetector.detectObjectFromImageBuffer(jpeg);
                    }
                });

                // start pumping jpegs out of the camera
                ffmpegProcess.stdout.pipe(picProcessor);
            }
        }
        catch (e) {
            logger.log(['ControllerService', 'error'], e.message);
        }
    }
}

export const controller = new ControllerService();
