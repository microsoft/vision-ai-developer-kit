// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for
// full license information.

const http = require('http');
const Process = require('child_process');
const io = require('socket.io')();
const fs = require('fs');
const dataRoot = 'CustomVision/data';

// A class that sets up a stream server, watches for web socket connections, controls lifetime
// of ffmpeg video streaming, and sends the video stream to clients connected over web sockets
class Mpeg4Stream {
    constructor(secret, streamingPort, wsPort) {
        this.secret = secret;
        this.streamingPort = streamingPort;
        this.wsPort = wsPort;
        this.ffmpegProcess = undefined;
        
        this.rtspUrl = null;

        // Check for default rtsp url in environment variables
        var rtspIp = process.env.RTSP_IP;
        var rtspPort = (process.env.RTSP_PORT) ? process.env.RTSP_PORT : '554';
        var rtspPath = (process.env.RTSP_PATH) ? process.env.RTSP_PATH : '';

        if (!rtspIp) {
            console.error(`Default rtsp stream has not been set: RTSP_IP=${rtspIp}, RTSP_PORT=${rtspPort}, RTSP_PATH=${rtspPath}`);
            return;
        } else if(!rtspPort) {
            rtspPort = '554';
        }
        
        this.rtspUrl = `rtsp://${rtspIp}:${rtspPort}/${rtspPath}`;

    }

    isVideoStreaming() {
        return this.ffmpegProcess !== undefined && !this.ffmpegProcess.killed;
    }

    // Send video stream over the configured camera to the specified streaming port on localhost
    startVideo() {
        if (!this.isVideoStreaming()) {

            if (!this.rtspUrl) {
                console.error(`RTSP path has not been provided.`);
                return;
            }

            const ffmpegParams = `-loglevel fatal -i ${this.rtspUrl} -vcodec copy -an -sn -dn -reset_timestamps 1 -movflags empty_moov+default_base_moof+frag_keyframe -bufsize 256k -f mp4 -seekable 0 -headers Access-Control-Allow-Origin:* -content_type video/mp4 http://127.0.0.1:${this.streamingPort}/${this.secret}`;
            console.log(`Running: ffmpeg ${ffmpegParams}`);

            this.ffmpegProcess = Process.spawn('ffmpeg', ffmpegParams.split(' '));

            this.ffmpegProcess.on('exit', function(code, signal) {
                console.log(`ffmpeg exited with code ${code} and signal ${signal}`);
            });
        }
    }

    // Stop video streaming
    stopVideo() {
        if (this.ffmpegProcess === undefined) {
            console.warn("Tried to stop video when ffmpeg wasn't known to be running");
            return;
        }

        const ffmpegProcess = this.ffmpegProcess;
        this.ffmpegProcess = undefined;
        ffmpegProcess.kill();

        if (process.platform === 'win32') {
            console.log('Running taskkill on ffmpeg to ensure all child processes are closed.');
            Process.exec('taskkill.exe /IM ffmpeg.exe /F');
        }
    }

    // Starts up the streaming server to listen to ffmpeg-source video stream, and relays that stream
    // to clients connected over web sockets
    startStreamingServer() {
        const self = this;

        io.on('connection', function(socket) {
            self.startVideo();

            if(socket.server.connectionCount == undefined)
            {
                socket.server.connectionCount = 1;
            }
            else
            {
                socket.server.connectionCount++;
            }

            console.log(`New client connected: total ${socket.server.connectionCount} clients.`);

            // Let the client know what the current rtsp stream is
            socket.emit('current-camera', self.rtspUrl);

            // Handle when the client chooses to change the rtsp stream
            socket.on('change-camera', function(rtspUrl) {
                self.rtspUrl = rtspUrl;
                self.stopVideo();
                self.startVideo();
                console.log(`Stream changed to: ${rtspUrl}`);
            })

            socket.on('disconnect', function(code, message) {
                // TODO: Add logic so multiple clients can receive the stream
                if(--socket.server.connectionCount == 0)
                {
                    console.log('Connected clients dropped to 0, so stopping video streaming');
                    self.stopVideo();
                    return;
                }
                console.log(`A client disconnected; (${socket.server.connectionCount} clients remaining).`);
            });
        });

        io.listen(this.wsPort);

        // HTTP Server to accept incoming mp4 stream from ffmpeg
        const streamServer = http.createServer(function(request, response) {
            const params = request.url.substr(1).split('/');

            if (params[0] !== self.secret) {
                console.error(`Failed stream connection: ${request.socket.remoteAddress}:${request.socket.remotePort} - wrong secret.`);
                response.end();
            }

            response.connection.setTimeout(0);
            console.log(`Stream connected at ${request.socket.remoteAddress}:${request.socket.remotePort}`);

            request.on('data', function(data) {
                io.emit('video-blob', data);
            });

            request.on('end', function() {
                console.log("Video stream closed.");
            });
        });

        streamServer.listen(this.streamingPort);

        console.log(`Listening for incoming mp4 stream on http://127.0.0.1:${this.streamingPort}/${this.secret}`);
        console.log(`Awaiting WebSocket connections on ws://127.0.0.1:${this.wsPort}`);
    }

    // Called by an event to capture images
    captureImage(payload) {
        // Parse payload for rtsp stream and tags
        var RTSP_IP = payload.RTSP_IP;
        var RTSP_PORT = (payload.RTSP_PORT) ? payload.RTSP_PORT : '554';
        var RTSP_PATH = payload.RTSP_PATH;
        var tags = payload.TAGS;

        // Save image for each tag
        for(var index in tags) {
            var tag = tags[index];
            var ffmpegCaptureProcess = null;

            // Make the folders
            fs.mkdir(dataRoot+'/'+tag, { recursive: true }, (err) => {
                if (err) {
                    console.log(err);
                }
                else {
                    console.log("Directory created successfully");
                }
            });

            // Capture the image
            const ffmpegParams = `-rtsp_transport tcp -y -i rtsp://${RTSP_IP}:${RTSP_PORT}/${RTSP_PATH} -vframes 1 -strftime 1 ${dataRoot}/${tag}/img-%m%d%y-%H%M%S.png`;
            console.log(`Running: ffmpeg ${ffmpegParams}`);

            ffmpegCaptureProcess = Process.spawn('ffmpeg', ffmpegParams.split(' '));

            ffmpegCaptureProcess.on('exit', function(code, signal) {
                console.log(`ffmpeg exited with code ${code} and signal ${signal}`);
            });

            // Output the errors
            ffmpegCaptureProcess.stderr.on('data', (err) => {
                console.log('err:', new String(err))
            });
        }
    }
}

module.exports = Mpeg4Stream;