import {
    platform as osPlatform,
    cpus as osCpus,
    freemem as osFreeMem,
    totalmem as osTotalMem
} from 'os';
import * as yargs from 'yargs';
import { logger } from './services/logger';
import { controller } from './services/controller';

process.on('unhandledRejection', (e) => {
    // tslint:disable:no-console
    console.log(['VisionAiDevKit', 'error'], `Excepction on startup... ${e.message}`);
    console.log(['VisionAiDevKit', 'error'], e.stack);
    // tslint:enable:no-console

    process.exit(-1);
});

async function start(args) {
    logger.log(['startup', 'info'], `🚀 Starting Vision AI Dev Kit...`);
    logger.log(['startup', 'info'], ` > Machine: ${osPlatform()}, ${osCpus().length} core, ` +
        `freemem=${(osFreeMem() / 1024 / 1024).toFixed(0)}mb, totalmem=${(osTotalMem() / 1024 / 1024).toFixed(0)}mb`);

    try {
        const context = {
            args
        };

        await controller.run(context);
    }
    catch (e) {
        logger.log(['startup', 'error'], `Error: ${e.message}`);
    }
}

const commandLineArgs = yargs
    .option('push-model', {
        alias: 'm',
        describe: 'Sets whether to push the model and required files to device or not',
        default: false
    })
    .option('ip-address', {
        alias: 'i',
        describe: 'IP address of the camera'
    })
    .option('username', {
        alias: 'u',
        describe: 'Username of account for access to the camera',
        required: true
    })
    .option('password', {
        alias: 'p',
        describe: 'Password of account for access to the camera',
        required: true
    })
    .argv;

start(commandLineArgs);
