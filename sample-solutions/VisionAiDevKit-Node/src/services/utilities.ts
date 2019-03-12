import { promisify } from 'util';
import { exec } from 'child_process';

class Utilities {
    public async getWlanIp() {
        const ifConfigFilter = `ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -f1 -d'/'`;
        const { stdout } = await promisify(exec)(ifConfigFilter, { encoding: 'utf8' });

        return (stdout || '127.0.0.1').trim();
    }
}

export const utilities = new Utilities();
