const http = require('http');
const ws = require('ws');
const Process = require('child_process');

// A class that sets up a stream server, watches for web socket connections, controls lifetime
// of ffmpeg video streaming, and sends the video stream to clients connected over web sockets
class Mpeg4Stream {
    constructor(secret, streamingPort, wsPort) {
        this.secret = secret;
        this.streamingPort = streamingPort;
        this.wsPort = wsPort;

        this.ffmpegProcess = undefined;
    }

    isVideoStreaming() {
        return this.ffmpegProcess !== undefined && !this.ffmpegProcess.killed;
    }

    // Send video stream over the configured camera to the specified streaming port on localhost
    startVideo() {
        if (!this.isVideoStreaming()) {
            const cameraIp = process.env.CAMERA_IP;
            const rtspPort = process.env.RTSP_PORT;
            const rtspPath = process.env.RTSP_PATH;

            if (!cameraIp || !rtspPort || !rtspPath) {
                console.error(`Necessary environment variables have not been set: CAMERA_IP=${cameraIp}, RTSP_PORT=${rtspPort}, RTSP_PATH=${rtspPath}`);
                return;
            }

            const rtspUrl = `rtsp://${cameraIp}:${rtspPort}/${rtspPath}`;
            const ffmpegParams = `-loglevel fatal -i ${rtspUrl} -vcodec copy -an -sn -dn -reset_timestamps 1 -movflags empty_moov+default_base_moof+frag_keyframe -bufsize 256k -f mp4 -seekable 0 -headers Access-Control-Allow-Origin:* -content_type video/mp4 http://127.0.0.1:${this.streamingPort}/${this.secret}`;
            console.log(ffmpegParams);

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
        this.socketServer = new ws.Server({ port: this.wsPort, perMessageDeflate: false });
        this.socketServer.connectionCount = 0;
        
        const self = this;

        this.socketServer.on('connection', function(socket, upgradeReq) {
            self.socketServer.connectionCount++;
            self.startVideo();

            const req = upgradeReq || socket.upgradeReq;
            console.log(`New client connected: ${req.socket.remoteAddress}, ${req.headers['user-agent']} (${self.socketServer.connectionCount} clients)`);

            // eslint-disable-next-line no-unused-vars
            socket.on('close', function(code, message) {
                if (--self.socketServer.connectionCount <= 0) {
                    console.log('Connected clients dropped to 0, so stopping video streaming');
                    self.stopVideo();
                    return;
                }

                console.log(`A client disconnected; (${self.socketServer.connectionCount} clients remaining)`);
            });
        });

        this.socketServer.broadcast = function(data) {
            self.socketServer.clients.forEach(function each(client) {
                if (client.readyState === ws.OPEN) {
                    client.send(data);
                }
            });
        };


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
                self.socketServer.broadcast(data);
            });

            request.on('end', function() {
                console.log("Stream closed.");
            });
        });

        streamServer.listen(this.streamingPort);

        console.log(`Listening for incoming mp4 stream on http://127.0.0.1:${this.streamingPort}/${this.secret}`);
        console.log(`Awaiting WebSocket connections on ws://127.0.0.1:${this.wsPort}`);
    }
}

module.exports = Mpeg4Stream;