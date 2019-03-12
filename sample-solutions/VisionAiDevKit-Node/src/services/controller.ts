import { logger } from './logger';
import { CameraClient } from '../sdk/camera';
import { FrameInference } from '../sdk/inferenceStream';
import { utilities } from './utilities';
import * as _get from 'lodash.get';

class ControllerService {
    // @ts-ignore (context)
    public async run(context: any) {
        logger.log(['controller', 'info'], `Starting capture processes`);

        try {
            const ipAddress = _get(context, 'args.ipAddress') || await utilities.getWlanIp();
            logger.log(['controller', 'info'], `Detected host ipAddress as: ${ipAddress}`);

            const cameraClient = await CameraClient.connect(context.args.username, context.args.username, ipAddress);

            cameraClient.on('inference', async(inference: FrameInference) => {
                logger.log(['controller', 'info'], `Inference: ${JSON.stringify(inference, null, 2)}`);

                const inferences = _get(inference, 'objects');
                if (inferences && Array.isArray(inferences)) {
                    for (const inferenceItem of inferences) {
                        logger.log(['controller', 'info'], `Inference: `
                            + `id:${_get(inferenceItem, 'id')} `
                            + `"${_get(inferenceItem, 'label')}" `
                            + `${_get(inferenceItem, 'confidence')}% `
                            + `[${_get(inferenceItem, 'x')}, `
                            + `${_get(inferenceItem, 'y')}, `
                            + `${_get(inferenceItem, 'width')}, `
                            + `${_get(inferenceItem, 'height')}]`);
                    }
                }
            });

            await cameraClient.getInferences();

            // tslint:disable-next-line: no-empty
            setInterval(() => {
                logger.log(['controller', 'info'], `Health check...`);
            }, 1000 * 15);
        }
        catch (ex) {
            logger.log(['ControllerService', 'error'], ex.message);
        }
    }
}

export const controller = new ControllerService();
