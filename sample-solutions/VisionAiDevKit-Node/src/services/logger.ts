import { config } from './config';

class LoggingService {
    private loggingFlag: string = '0';

    constructor() {
        this.loggingFlag = config.get('loggingFlag');
    }

    public log(tags: any, message: any) {
        if (!this.loggingFlag) {
            return;
        }

        const tagsMessage = tags ? (Array.isArray(tags)) ? `[${tags.join(', ')}]` : `[${tags}]` : `[]`;

        // tslint:disable-next-line:no-console
        console.log(tagsMessage, message);
    }
}

export const logger = new LoggingService();
