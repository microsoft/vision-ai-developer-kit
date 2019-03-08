import { resolve as pathResolve } from 'path';
import * as nconf from 'nconf';
import { logger } from './logger';

class ConfigService {
    private config: nconf.Provider;

    // @ts-ignore (context)
    public async init(context: any) {
        if (typeof context === 'object'
            && !!context
            && context.projectRoot) {
            this.config = nconf.env().file(pathResolve(context.projectRoot, `configs/${process.env.NODE_ENV}.json`));
        }

        logger.log(['config', 'info'], `Service initialized`);
    }

    public get(key: string): any {
        return this.config.get(key);
    }
}

export const config = new ConfigService();
