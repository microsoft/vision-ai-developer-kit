// Copyright (c) 2018, The Linux Foundation. All rights reserved.
// Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
// full license information.

// This module provides APIs for communicating with QMMF IPC webserver.

import * as request from 'request';
import { logger } from './logger';

export default class IpcProvider {
    private username: string;
    private password: string;
    private ipAddress: string;
    private port: string;
    private sessionToken: string;

    constructor(username: string, password: string, ipAddress: string) {
        this.username = username;
        this.password = password;
        this.ipAddress = ipAddress;

        // Port over which the camera/QMMF IPC webserver communicates
        this.port = '1080';

        // Session identifier obtained from the camera/QMMF IPC webserver
        this.sessionToken = undefined;
    }

    // GET API for QMMF IPC webserver.
    //
    // Parameters
    // ----------
    // path : str
    //     QMMF IPC webserver API.
    //
    // Returns
    // -------
    // object
    //     Response
    //
    // Exception
    //     Any exception that occurs during the request.

    public async get(path: string): Promise<any> {
        try {
            const options = {
                method: 'GET',
                url: `http://${this.ipAddress}:${this.port}${path}`,
                headers: {
                    Cookie: this.sessionToken
                }
            };

            logger.log(['ipcProvider', 'info'], `API: ${options.url}, data:${options.body}`);

            const response = await this.ipcRequest(options);

            logger.log(['ipcProvider', 'info'], `RESPONSE: ${response}`);

            return response;
        }
        catch (ex) {
            logger.log(['ipcProvider', 'error'], ex.message);

            throw new Error(ex.message);
        }
    }

    // POST API for QMMF IPC webserver.
    //
    // Parameters
    // ----------
    // path : str
    //     QMMF IPC webserver API.
    // payload : str
    //     JSON payload for the `path` API.
    //
    // Returns
    // -------
    // object
    //     Response
    //
    // Exception
    //     Any exception that occurs during the request.

    public async post(path: string, payload: any): Promise<any> {
        try {
            const options = {
                method: 'POST',
                url: `http://${this.ipAddress}:${this.port}${path}`,
                headers: {
                    Cookie: this.sessionToken
                },
                json: true,
                body: payload
            };

            logger.log(['ipcProvider', 'info'], `API: ${options.url}, data:${options.body}`);

            const response = await this.ipcRequest(options);

            logger.log(['ipcProvider', 'info'], `RESPONSE: ${response}`);

            return response;
        }
        catch (ex) {
            logger.log(['ipcProvider', 'error'], ex.message);

            throw new Error(ex.message);
        }
    }

    // Establish a connection with QMMF IPC webserver on the camera.
    //
    // This API also sets the `sessionToken` attribute from the token
    // obtained from the camera.
    //
    // Returns
    // -------
    // object
    //     Response
    //
    // Timeout
    //     When the request times out on the connect request.
    //
    // RequestException
    //     The request is not correctly formed.

    public async connect() {
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

            logger.log(['ipcProvider', 'info'], `API: ${options.url}, data:${options.body}`);

            const response = await this.ipcRequest(options);

            logger.log(['ipcProvider', 'info'], `RESPONSE: ${response}`);

            if (response.status) {
                this.sessionToken = response.headers['Set-Cookie'];
            }

            return response;
        }
        catch (ex) {
            logger.log(['ipcProvider', 'error'], ex.message);

            throw new Error(ex.message);
        }
    }

    // Logout from the QMMF IPC webserver on the camera.
    //
    // Returns
    // -------
    // object
    //     Response
    //
    // Exception
    //     Any exception that occurs during the request.

    public async logout() {
        try {
            const options = {
                method: 'POST',
                url: `http://${this.ipAddress}:${this.port}/logout`,
                json: true,
                body: {}
            };

            logger.log(['ipcProvider', 'info'], `API: ${options.url}, data:${options.body}`);

            const response = await this.ipcRequest(options);

            logger.log(['ipcProvider', 'info'], `RESPONSE: ${response}`);

            return response;
        }
        catch (ex) {
            logger.log(['ipcProvider', 'error'], ex.message);

            throw new Error(ex.message);
        }
    }

    private async ipcRequest(options): Promise<any> {
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

                return resolve(body);
            });
        });
    }
}
