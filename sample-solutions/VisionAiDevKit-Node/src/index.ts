import {
    platform as osPlatform,
    cpus as osCpus,
    freemem as osFreeMem,
    totalmem as osTotalMem
} from 'os';
import { resolve as pathResolve } from 'path';
import { logger } from './services/logger';
import { config } from './services/config';
import { controller } from './services/controller';

process.on('unhandledRejection', (e) => {
    // tslint:disable:no-console
    console.log(['iotc-persondetector', 'error'], `Excepction on startup... ${e.message}`);
    console.log(['iotc-persondetector', 'error'], e.stack);
    // tslint:enable:no-console

    process.exit(-1);
});

async function start() {
    logger.log(['startup', 'info'], `🚀 Starting Vision AI Dev Kit...`);
    logger.log(['startup', 'info'], ` > Machine: ${osPlatform()}, ${osCpus().length} core, ` +
        `freemem=${(osFreeMem() / 1024 / 1024).toFixed(0)}mb, totalmem=${(osTotalMem() / 1024 / 1024).toFixed(0)}mb`);

    try {
        const context = {
            projectRoot: pathResolve(__dirname, '../..')
        };

        await config.init(context);

        await controller.run(context);
    }
    catch (e) {
        logger.log(['startup', 'error'], `Error: ${e.message}`);
    }
}

start();
