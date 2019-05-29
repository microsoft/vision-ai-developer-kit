// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for
// full license information.

const mediaSource = new MediaSource();
const queue = [];
const video = document.querySelector('video');
var pauseState = true;

var websocket;
var buffer;

function OnClickPlay() {
    console.log('OnClickPlay fired.');
    document.getElementById("playButton").style.display = "none";
    if (!pauseState) {
        return;
    }
    pauseState = false;
    websocket = new WebSocket('ws://' + document.location.hostname + ':3002');
    websocket.binaryType = 'arraybuffer';
    websocket.onopen = function (event) {
        console.log("Connection established");
        video.src = window.URL.createObjectURL(mediaSource);
    }

    websocket.addEventListener('message', function (e) {
        if (buffer && typeof e.data !== 'string') {
            if (buffer.updating || queue.length > 0) {
                queue.push(e.data);
            } else {
                buffer.appendBuffer(e.data);
            }
        }
    }, false);
}

document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
        websocket.close();
        pauseState = true;
    } else {
        OnClickPlay();
    }
}, false);

video.addEventListener("pause", function () {
    websocket.close();
    pauseState = true;
}, false);

video.addEventListener("play", function () {
    if (pauseState === true) {
        OnClickPlay();
    }
}, false);

mediaSource.addEventListener('sourceopen', function (e) {
    console.log('MediaSource sourceopen fired: ' + mediaSource.readyState);
    video.play();
    // buffer = mediaSource.addSourceBuffer('video/mp4; codecs="avc1.42E01E"');  //mp4a.40.29
    // buffer = mediaSource.addSourceBuffer('video/mp4 codecs="avc1.64000d, mp4a.40.2"');
    buffer = mediaSource.addSourceBuffer('video/mp4; codecs="avc1.42E01E"');
    buffer.addEventListener('updatestart', function (e) {
        // console.log('buffer updatestart: ' + mediaSource.readyState);
    });
    buffer.addEventListener('update', function (e) {
        // console.log('buffer update: ' + mediaSource.readyState);
    });
    buffer.addEventListener('updateend', function (e) {
        // console.log('buffer updateend: ' + mediaSource.readyState);
    });
    buffer.addEventListener('error', function (e) {
        console.log('buffer error: ' + mediaSource.readyState);
    });
    buffer.addEventListener('abort', function (e) {
        console.log('buffer abort: ' + mediaSource.readyState);
    });
    buffer.addEventListener('update', function (e) { // Note: Have tried 'updateend'
        if (queue.length > 0 && !buffer.updating) {
            buffer.appendBuffer(queue.shift());
        }
    });
}, false);

mediaSource.addEventListener('sourceended', function (e) {
    console.log('sourceended: ' + mediaSource.readyState);
});
mediaSource.addEventListener('sourceclose', function (e) {
    console.log('sourceclose: ' + mediaSource.readyState);
});
mediaSource.addEventListener('error', function (e) {
    console.log('sourceerror: ' + mediaSource.readyState);
});

const promise = video.play();
if (promise !== undefined) {
    promise.then(_ => {
        // Autoplay started!
    }).catch(error => {
        // Autoplay was prevented.
        // Show a "Play" button so that user can start playback.
        document.getElementById("playButton").style.display = null;
    });
}