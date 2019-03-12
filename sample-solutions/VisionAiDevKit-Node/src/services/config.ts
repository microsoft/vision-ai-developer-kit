import { resolve as pathResolve } from 'path';
import * as nconf from 'nconf';

class ConfigService {
    private config: nconf.Provider;

    constructor() {
        this.config = nconf.env().file(pathResolve(__dirname, '../..', `configs/${process.env.NODE_ENV}.json`));
    }

    public get(key: string): any {
        return this.config.get(key);
    }
}

export const config = new ConfigService();
