import React, { Component } from 'react';
import axios from 'axios';
import '../styles/viewing.css';
import AppWithSideBar from '../components/sidebar'
import AddCamera from "../components/add-camera"
import openSocket from 'socket.io-client';

// The path to the server
const server_port = (process.env.REACT_APP_SERVER_PORT) ? process.env.REACT_APP_SERVER_PORT : '3003';
const wsPort = (process.env.REACT_APP_WEB_SOCKET_PORT) ? process.env.REACT_APP_WEB_SOCKET_PORT : '3002';
const path = `http://${document.location.hostname}:${server_port}`;


/**
 * This is the page from which you can view the
 * rtsp stream, change streams, and capture and
 * tag an image.
 */
class ViewingPage extends Component {

  constructor(props) {
    super(props)
    this.state = {
      message: 'Live Stream ',
      saveMessage: '',
      isVideoStreaming: false,
      mediaSource: new MediaSource(),
      queue: [],
      buffer: null,
      filenames: [],
      socket: openSocket(`http://${document.location.hostname}:${wsPort}`), // Socket for ffmpeg data
      cameras: [],
      currentCamIp: 'Select Camera'
    }
  }

  sidebarOptions = [
    {
      name: 'Live Stream ',
      handleClick: () => { 
        this.props.history.push('/')
      },
      children: [],
      isActive: true
    },
    {
      name: 'Review',
      handleClick: () => {
        this.state.socket.disconnect();
        this.props.history.push('/review');
      },
      children: []
    },
    {
      name: 'Push to Custom Vision',
      handleClick: () => {
        this.state.socket.disconnect();
        this.props.history.push('/push-custom-vision');
      },
      children: []
    },
    {
      name: 'Push to Blob Store',
      handleClick: () => {
        this.state.socket.disconnect();
        this.props.history.push('/push-blob-store');
      },
      children: []
    }
  ];

  componentWillMount = () => {
    var self = this;

    // Create data and metadata folders
    axios.post(path+'/viewing/set-up');

    // Get the cameras
    axios
    .post(path+'/viewing/get-cameras')
    .then(response => {
      console.log(response.data);
      this.setState({
        cameras: response.data
      });
    })
    .catch(rejected => {
      console.log(rejected);
    });

    // Get the names of all files already saved
    axios
    .post(path+'/viewing/filenames')
    .then(response => {
      this.setState({ 
        filenames: response.data
      }); 
    })
    .catch(rejected => {
      console.log(rejected);
    });

    /** Set up Socket Logic **/
    this.state.socket.on('connect', function() {
      self.onSocketOpen();
    });

    // Receiving data from the livestream
    this.state.socket.on('video-blob', data => {
      self.handleData(data);
    });

    // Receiving the URL of the current camera
    this.state.socket.on('current-camera', rtspUrl => {
      console.log("Current camera url received: ", rtspUrl);
      self.handleCurrentRtspUrl(rtspUrl);
    });
  }

  onSocketOpen = () => {
    console.log("Socket Open");

    var {buffer, queue, mediaSource} = this.state;
    var self = this;

    mediaSource = new MediaSource();

    mediaSource.addEventListener('sourceopen', function (e){
      console.log('MediaSource sourceopen fired: ' + mediaSource.readyState);

      // Begin playing the video when the media source is opened
      const playPromise = self.refs.vidRef.play();
      if (playPromise !== undefined) {
        playPromise.then(_ => {
            // Autoplay started!
        }).catch(error => {
            // Autoplay was prevented.
        });
      }

      buffer = mediaSource.addSourceBuffer('video/mp4; codecs="avc1.42E01E"');
      console.log(buffer);
      self.setState({
        buffer: buffer
      });

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
      buffer.addEventListener('update', function (e) {
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

    // Handle visibility change
    document.addEventListener("visibilitychange", function () {
      if(document.hidden) {
        self.state.socket.disconnect();
      }
      else {
        self.state.socket.connect();
      }
    }, false);

    // Update state
    this.setState({
      mediaSource: URL.createObjectURL(mediaSource),
      isVideoStreaming: true
    });
  }

  /*
   * Receive data and append it to video source buffer
   */
  handleData = (data) => {
    var {buffer, queue} = this.state;

    if (buffer && typeof data !== 'string') {
      if (buffer.updating || queue.length > 0) {
        queue.push(data);
      } else {
        buffer.appendBuffer(data);
      }
    }
  }

  /*
   * Capture Image just as a canvas from the video source
   */
  onClickCapture = () => {
    if(this.state.isVideoStreaming) {
      var ctx = this.refs.captureCanvas.getContext('2d');
      ctx.drawImage(this.refs.vidRef, 0, 0, 880, 580);

      this.setState({
        message: "Image Captured",
        saveMessage: '',
        isVideoStreaming: false
      });
    }
  }

  /**
   * Save the canvas image to disk
   */
  onSaveImage = (e) => {
    // Keep the form from POSTing
    e.preventDefault();

    // Get the image name
    const imageName = this.refs.imageName.value;

    // Error if no image name was entered
    if(!imageName){
      this.setState({
        saveMessage: 'Please enter an image name.'
      });
      return;
    }

    // Error if this image name already exists
    if(this.state.filenames.includes(imageName+'.png'))
    {
      this.setState({
        saveMessage: 'This image name already exists.'
      });
      return;
    }

    // Get the image and tags
    const image = this.refs.captureCanvas.toDataURL('image/png', 1.0);
    const tags = document.getElementsByName('tag');

    var hasTag = false;
    for(const tag of tags) {
      var tagLength = tag.value.length;

      // Save image for each tag
      if(tagLength >= 1) {
        hasTag = true;

        axios
        .post(path+'/viewing/capture',
        {
          image: image,
          tag: tag.value,
          imageName: imageName
        })
        .then(response => {
          this.setState({ 
            message: 'Live Stream ',
            saveMessage: response.data,
            isVideoStreaming: true
          });

          // Store the image name
          if(!this.state.filenames.includes(imageName+'.png'))
          {
            this.state.filenames.push(imageName+'.png');
          }
        })
        .catch(rejected => {
          console.log(rejected);
        });
      }
    }

    // There must be at least one tag
    if(!hasTag){
      this.setState({
        saveMessage: 'Please enter a tag name.'
      });
      return;
    }
  }

  /**
   * Return to the live stream
   */
  onClickCancel = () => {
    this.setState({ 
      message: 'Live Stream ',
      saveMessage: '',
      isVideoStreaming: true
    });
  }

  /**
   * Dynamically add tags to the input form
   */
  onClickAddTag = () => {
    console.log("Adding tag input field.");
    
    // Create the input element
    var inputElem = document.createElement("input");
    inputElem.setAttribute('type', 'text');
    inputElem.setAttribute('id', 'tag');
    inputElem.setAttribute('name', 'tag');
    inputElem.setAttribute('placeholder', 'Tag...');

    // Create a <br/> element
    var brElem = document.createElement("br");

    // Get the right divs
    var tagInputs = document.getElementById('tag-form');
    var imageNameElem = document.getElementById('image-name');

    // Add the input element to the right div
    tagInputs.insertBefore(inputElem, imageNameElem);
    tagInputs.insertBefore(brElem, imageNameElem);
  }

  /**
   * Add the camera to the array of cameras
   */
  onAddCamera = (form, e) => {
    // Keep the form from POSTing
    e.preventDefault();

    // Get the existing cameras
    var camArray = [...this.state.cameras];
    camArray.push({
      name: form.camName.value,
      rtspAddress: form.rtspAddress.value
    });

    // Save the camera to the state
    this.setState({
      cameras: camArray
    });

    // Write the cameras to file for permanent storage
    axios
    .post(path+'/viewing/save-camera', {
      cameras: camArray
    })
    .then(response => {
      console.log("Cameras saved"); 
    })
    .catch(rejected => {
      console.log(rejected);
    });

    form.reset();
  }

  /**
   * Send the new rtsp stream to the server
   */
  onSelectCamera = (e) => {
    console.log("Stream selected: ", e.target.value);

    // Change the IP of the live stream on the server side
    this.state.socket.emit('change-camera', e.target.value);
    this.state.socket.disconnect();
  }

  /**
   * Save the url of the current rtsp stream
   */
  handleCurrentRtspUrl = (rtspUrl) => {
    var { cameras } = this.state;
    
    // If there is no rtsp stream, just return
    if(!rtspUrl) {
      return;
    }

    // Update the state with the current camera
    this.setState({
      currentCamIp: rtspUrl
    });

    // Check if the rtspUrl already exists in the array of cameras
    for(var cam in cameras) {
      if(cameras[cam].rtspAddress === rtspUrl) {
        return;
      }
    }

    // Else add it to the array of cameras
    var camArray = [...this.state.cameras];
    camArray.push({
      name: 'Default',
      rtspAddress: rtspUrl
    });

    this.setState({
      cameras: camArray
    });
  }

  /**
   * Reconnect the socket on camera start
   */ 
  onStartCamera = () => {
    this.state.socket.connect();
  }

  render() {
    const {message, mediaSource, isVideoStreaming, saveMessage, currentCamIp} = this.state;

    return (
      <AppWithSideBar listElements={this.sidebarOptions} >
        {/* Live stream and Captured Image */}
        <div className="view-container">
          <div className="video-container">
            <canvas ref="captureCanvas" className="capture-canvas" width={880} height={580} hidden={(isVideoStreaming) ? 'hidden' : ''}/>
            <video ref='vidRef' key={mediaSource} hidden={(isVideoStreaming) ? '' : 'hidden'} controls autoPlay playsInline={true} muted="muted">
              <source src={mediaSource}/>
            </video>
            <button ref='playButton' onClick={this.playVideo} hidden={true}>Play</button>
            <h3>{message}{(isVideoStreaming) && currentCamIp}</h3>
          </div>

          {/* Change Camera and Capture Image options */}
          <div className="capture-container">
            <AddCamera 
              listElements={this.state.cameras}
              handleSelect={this.onSelectCamera}
              handleAddCam={this.onAddCamera}
              handleSave={this.onStartCamera}
              currentCamIp={currentCamIp}
            /><br/>

            <button className="capture-button" onClick={this.onClickCapture}>Capture</button>
            { !isVideoStreaming && (
              <form className="tag-form" id="tag-form" method="post" onSubmit={this.onSaveImage}>
                <input type="text" id="tag" name="tag" ref="tag" placeholder="Tag..."/><br/>
                <input type="text" id="image-name" ref="imageName" placeholder="Image Name..."/><br/>
                <input type="button" ref="add-tag" value="Add Tag" onClick={this.onClickAddTag}/><br/>
                <input type="submit" value="Save Image"/><br/>
                <input type="button" ref="cancel" value="Cancel" onClick={this.onClickCancel}/>
              </form>
            )}
            <h4>{saveMessage}</h4>
          </div>
        </div>
      </AppWithSideBar>
    );
  }
}

export default ViewingPage;
