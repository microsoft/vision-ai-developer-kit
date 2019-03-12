// Copyright (c) 2018, The Linux Foundation. All rights reserved.
// Licensed under the BSD License 2.0 license. See LICENSE file in the project root for
// full license information.

// This module provides iterator for getting frame and inference.

import { spawn } from 'child_process';
import { EventEmitter } from 'events';
import { Transform } from 'stream';
import { logger } from '../services/logger';

const gStreamerCommand = 'gst-launch-1.0';
const gStreamerCommandArgs = '-q rtspsrc location=###INFERENCE_SRC_URL protocols=tcp ! application/x-rtp, media=application ! fakesink dump=true';
const chunkHeader0 = '00000000';
const startOfInference = '{ "t';

export interface FrameInference {
    timestamp: number;
    objects: FrameInferenceObject[];
}

export interface FrameInferenceObject {
    id: number;
    label: string;
    confidence: number;
    position: FrameInferenceObjectPosition;
}

export interface FrameInferenceObjectPosition {
    x: number;
    y: number;
    width: number;
    height: number;
}

class InferenceProcessor extends Transform {
    private inferenceLines: any[];

    constructor(options: any) {
        super(options);

        this.inferenceLines = [];
    }

    // @ts-ignore (encoding)
    public _transform(chunk: Buffer, encoding: string, done: callback) {
        const chunkString = chunk.toString('utf8');
        if (chunkString.substring(0, 8) !== chunkHeader0) {
            const chunkLines = chunkString.split('\n');
            for (const chunkLine of chunkLines) {
                this.inferenceLines.push(chunkLine.substring(74).trim());
            }

            try {
                const inference = JSON.parse(this.inferenceLines.join(''));

                if ((this as any)._readableState.pipesCount > 0) {
                    this.push(inference);
                }

                if (this.listenerCount('inference') > 0) {
                    this.emit('inference', inference);
                }
            }
            catch (ex) {
                logger.log(['frameIterator', 'error'], `Malformed inference data: ${this.inferenceLines.join('')}`);
            }

            this.inferenceLines = [];
        }
        else {
            const startIndex = chunkString.indexOf(startOfInference);
            if (startIndex !== -1) {
                this.inferenceLines.push(startOfInference);

                const chunkLines = chunkString.substring(92).split('\n');
                for (const chunkLine of chunkLines) {
                    if (chunkLine.substring(0, 8) !== chunkHeader0) {
                        this.inferenceLines.push(chunkLine.substring(74).trim());
                    }
                }
            }
        }

        return done();
    }
}

export class InferenceStreamProcessor extends EventEmitter {
    private gStreamerProcess: any;

    constructor() {
        super();

        this.gStreamerProcess = undefined;
    }

    public start(inferenceSrcUrl: string) {
        const gStreamerCommandArgsWithLocation = gStreamerCommandArgs.replace('###INFERENCE_SRC_URL', inferenceSrcUrl)
        this.gStreamerProcess = spawn(gStreamerCommand, gStreamerCommandArgsWithLocation.split(' '), { stdio: ['ignore', 'pipe', 'ignore'] });

        this.gStreamerProcess.on('error', (error) => {
            logger.log(['frameIterator', 'error'], `gStreamerProcess.on(error): ${error}`);
        });

        this.gStreamerProcess.on('exit', (code, signal) => {
            logger.log(['frameIterator', 'info'], `gStreamerProcess.on(exit), code: ${code}, signal: ${signal}`);
        });

        const frameInferenceProcessor = new InferenceProcessor({});

        frameInferenceProcessor.on('inference', async(inference: FrameInference) => {
            if (this.listenerCount('inference') > 0) {
                this.emit('inference', inference);
            }
        });

        // start processing the inference data stream
        this.gStreamerProcess.stdout.pipe(frameInferenceProcessor);
    }

    public stop() {
        if (this.gStreamerProcess) {
            this.gStreamerProcess.stdout.pause();
            this.gStreamerProcess.kill();
        }
    }
}
