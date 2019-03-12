// Copyright (c) 2018, The Linux Foundation. All rights reserved.
// Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
// full license information.

// This module provides APIs for communicating with QMMF IPC webserver.

import * as request from 'request';
import * as _get from 'lodash.get';
import { logger } from '../services/logger';

export class IpcProvider {
    public static getInstance(username: string, password: string, ipAddress: string) {
        return this.instance || (this.instance = new this(username, password, ipAddress));
    }

    private static instance: IpcProvider;

    private username: string;
    private password: string;
    private ipAddress: string;
    private port: string;
    private sessionToken: string;

    private constructor(username: string, password: string, ipAddress: string) {
        this.username = username;
        this.password = password;
        this.ipAddress = ipAddress;

        // Port over which the camera/QMMF IPC webserver communicates
        this.port = '1080';

        // Session identifier obtained from the camera/QMMF IPC webserver
        this.sessionToken = '';
    }

    public async ipcLogin(): Promise<any> {
        try {
            const options = {
                method: 'POST',
                url: `http://${this.ipAddress}:${this.port}/login`,
                json: true,
                body: {
                    username: this.username,
                    userpwd: this.password
                }
            };

            logger.log(['ipcProvider', 'info'], `LOGIN API: ${options.url}`);

            const result = await this.timerTest(options);

            logger.log(['ipcProvider', 'info'], `RESPONSE HEADERS: ${result.response.headers}`);
            logger.log(['ipcProvider', 'info'], `RESPONSE BODY: ${result.body}`);

            if (result.body.status === true) {
                this.sessionToken = _get(result, 'response.headers[set-cookie][0]');
            }

            return result.body;
        }
        catch (ex) {
            logger.log(['ipcProvider', 'error'], ex.message);

            throw new Error(ex.message);
        }
    }

    public async ipcLogout() {
        return this.ipcPostRequest('/logout');
    }

    public ipcGetRequest(path: string, params?: string) {
        return this.ipcRequest('GET', path, params);
    }

    public async ipcPostRequest(path: string, payload?: any, params?: string) {
        return this.ipcRequest('POST', path, params, payload);
    }

    public async ipcRequest(method: string, path: string, params: string, payload?: any): Promise<any> {
        try {
            const url = params ? `${path}?${params}` : path;
            const options = {
                method,
                url: `http://${this.ipAddress}:${this.port}${url}`,
                headers: {
                    Cookie: this.sessionToken
                }
            };

            if (method === 'POST' && payload) {
                Object.assign(options, {
                    json: true,
                    body: payload
                });
            }

            logger.log(['ipcProvider', 'info'], `API: ${options.url}`);

            const result = await this.makeRequest(options);

            logger.log(['ipcProvider', 'info'], `RESPONSE: ${result.body}`);

            return result.body;
        }
        catch (ex) {
            logger.log(['ipcProvider', 'error'], ex.message);

            throw new Error(ex.message);
        }
    }

    private async timerTest(options: any): Promise<any> {
        return new Promise((resolve) => {
            setTimeout(() => {
                return resolve({
                    headers: {
                        foo: 5,
                        bar: 2
                    },
                    body: {
                        status: false
                    }
                });
            }, 2000);
        });
    }

    private async makeRequest(options): Promise<any> {
        return new Promise((resolve, reject) => {
            request(options, (requestError, response, body) => {
                if (requestError) {
                    logger.log(['ipcProvider', 'error'], `hueRequest: ${requestError.message}`);
                    return reject(requestError);
                }

                if (response.statusCode < 200 || response.statusCode > 299) {
                    logger.log(['ipcProvider', 'error'], `Response status code = ${response.statusCode}`);

                    const errorMessage = body.message || body || 'An error occurred';
                    return reject(new Error(`Error statusCode: ${response.statusCode}, ${errorMessage}`));
                }

                return resolve({
                    response,
                    body
                });
            });
        });
    }
}
