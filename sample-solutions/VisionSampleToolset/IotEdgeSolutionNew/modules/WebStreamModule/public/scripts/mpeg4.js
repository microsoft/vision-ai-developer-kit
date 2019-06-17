/* eslint-disable no-unused-vars */
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for
// full license information.

const mediaSource = new MediaSource();
const queue = [];
const video = document.querySelector('video');
let isPaused = true;

var websocket;
var buffer;

function OnClickPlay() {
    console.log('OnClickPlay fired.');
    document.getElementById('playButton').style.display = 'none';
    if (!isPaused) {
        return;
    }
    isPaused = false;
    websocket = new WebSocket('ws://' + document.location.hostname + ':3002');
    websocket.binaryType = 'arraybuffer';
    websocket.onopen = (event) => {
        try {
            console.log('Connection established.');
            video.src = window.URL.createObjectURL(mediaSource);
        } catch (err) {
            console.error('Exception opening websocket!');
            console.log(err);
        }
    }

    websocket.addEventListener('message', (e) => {
        try {
            if (buffer && typeof e.data !== 'string') {
                if (buffer.updating || queue.length > 0) {
                    queue.push(e.data);
                } else {
                    buffer.appendBuffer(e.data);
                }
            }
        } catch (err) {
            console.error('Exception in websocket message!');
            console.log(err);
        }
    }, false);

    websocket.onerror = (event) => {
        console.error('WebSocket error!');
        console.log(event);
        console.log('WebSocket ready state: ' + websocket.readyState);
    }

    websocket.onclose = (event) => {
        var reason;
        // See http://tools.ietf.org/html/rfc6455#section-7.4.1
        if (event.code == 1000)
            reason = `Normal closure, meaning that the purpose for which the connection was established has been fulfilled.`;
        else if (event.code == 1001)
            reason = `An endpoint is "going away", such as a server going down or a browser having navigated away from a page.`;
        else if (event.code == 1002)
            reason = `An endpoint is terminating the connection due to a protocol error`;
        else if (event.code == 1003)
            reason = `An endpoint is terminating the connection because it has received a type of data it cannot accept (e.g., an endpoint that understands only text data MAY send this if it receives a binary message).`;
        else if (event.code == 1004)
            reason = `Reserved. The specific meaning might be defined in the future.`;
        else if (event.code == 1005)
            reason = `No status code was actually present.`;
        else if (event.code == 1006)
            reason = `The connection was closed abnormally, e.g., without sending or receiving a Close control frame`;
        else if (event.code == 1007)
            reason = `An endpoint is terminating the connection because it has received data within a message that was not consistent with the type of the message (e.g., non-UTF-8 [http://tools.ietf.org/html/rfc3629] data within a text message).`;
        else if (event.code == 1008)
            reason = `An endpoint is terminating the connection because it has received a message that "violates its policy". This reason is given either if there is no other sutible reason, or if there is a need to hide specific details about the policy.`;
        else if (event.code == 1009)
            reason = `An endpoint is terminating the connection because it has received a message that is too big for it to process.`;
        else if (event.code == 1010) // Note that this status code is not used by the server, because it can fail the WebSocket handshake instead.
            reason = `An endpoint (client) is terminating the connection because it has expected the server to negotiate one or more extension, but the server didn't return them in the response message of the WebSocket handshake. <br /> Specifically, the extensions that are needed are: ` + event.reason;
        else if (event.code == 1011)
            reason = `A server is terminating the connection because it encountered an unexpected condition that prevented it from fulfilling the request.`;
        else if (event.code == 1015)
            reason = `The connection was closed due to a failure to perform a TLS handshake (e.g., the server certificate can't be verified).`;
        else
            reason = `Unknown reason`;

        console.error('WebSocket closed due to: ' + reason);
        console.log(event);
    }
}

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        websocket.close();
        isPaused = true;
    } else {
        OnClickPlay();
    }
}, false);

video.addEventListener('pause', () => {
    websocket.close();
    isPaused = true;
}, false);

video.addEventListener('play', () => {
    if (isPaused) {
        OnClickPlay();
    }
}, false);

mediaSource.addEventListener('sourceopen', (e) => {
    console.log('MediaSource sourceopen fired: ' + mediaSource.readyState);

    buffer = mediaSource.addSourceBuffer('video/mp4; codecs="avc1.42E01E"');
    video.addEventListener('canplay', () => { video.play(); });

    buffer.addEventListener('error', (e) => {
        console.error('Buffer error!');
        console.log(e);
    });
    buffer.addEventListener('abort', (e) => {
        console.error('Buffer abort!');
        console.log(e);
    });
    buffer.addEventListener('update', (e) => { // Note: Have tried 'updateend'
        if (queue.length > 0 && !buffer.updating) {
            buffer.appendBuffer(queue.shift());
        }
    });
}, false);

mediaSource.addEventListener('sourceended', (e) => {
    console.log('Source ended.');
    console.log(e);
});
mediaSource.addEventListener('sourceclose', (e) => {
    console.log('Source closed.');
    console.log(e);
});
mediaSource.addEventListener('error', (e) => {
    console.error('Source error!');
    console.log(e);
});

const promise = video.play();
if (promise !== undefined) {
    promise.then(_ => {
        // Autoplay started!
    }).catch(error => {
        // Autoplay was prevented.
        // Show a "Play" button so that user can start playback.
        document.getElementById('playButton').style.display = null;
        console.error('Autoplay failed due to: ' + error);
    });
}