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

console.log(`Viewing:: opening socket - http://${document.location.hostname}:${wsPort}`);

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
      mediaSource: null,
      queue: [],
      buffer: null,
      filenames: [],
      socket: openSocket(`http://${document.location.hostname}:${wsPort}`), // Socket for ffmpeg data
      cameras: [],
      currentCamIp: '- Need to setup Camera -',
      selectedCamIp: "",
      resetStream: false
    }
  }

  sidebarOptions = [
    {
      name: 'Capture',
      handleClick: () => { 
        this.props.history.push('/')
      },
      children: [],
      isActive: true
    },
    {
      name: 'Images',
      handleClick: () => {
        this.state.socket.disconnect();
        this.props.history.push('/review');
      },
      children: []
    },
    {
      name: 'Upload Settings',
      handleClick: () => {
        this.state.socket.disconnect();
        this.props.history.push('/upload');
      },
      children: []
    }
  ];

  UNSAFE_componentWillMount = () => {
    var self = this;

    /** Set up Socket Logic **/
    this.state.socket.on('connect', () => {
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

  /**
   * Sets up logic for receiving data through the
   * web socket for the video stream.
   */
  onSocketOpen = () => {
    console.log(`Viewing::Socket Open - http://${document.location.hostname}:${wsPort}`);

    var {buffer, queue, mediaSource} = this.state;
    var self = this;

    self.getPageInitSetting();

    if(mediaSource === null)
    {
      mediaSource = new MediaSource();
      mediaSource.addEventListener('sourceopen', function (e){
        console.log('MediaSource sourceopen fired: ' + mediaSource.readyState);
  
        if (mediaSource.sourceBuffers.length === 0)
        {
          buffer = mediaSource.addSourceBuffer('video/mp4; codecs="avc1.42E01E"');
          buffer.mode = "sequence";
    
          self.setState({
            buffer: buffer
          });
    
          buffer.addEventListener('updatestart', function (e) {
              //console.log('buffer updatestart: ' + mediaSource.readyState);
          });
          buffer.addEventListener('update', function (e) {
              //console.log('buffer update: ' + mediaSource.readyState + ', queue length: ' +queue.length);;
              if (queue.length > 0 && !buffer.updating) {
                buffer.appendBuffer(queue.shift());
              }
          });
          buffer.addEventListener('updateend', function (e) {
              //console.log('buffer updateend: ' + mediaSource.readyState);
          });
          buffer.addEventListener('error', function (e) {
              console.log('buffer error: ' + mediaSource.readyState);
          });
          buffer.addEventListener('abort', function (e) {
              console.log('buffer abort: ' + mediaSource.readyState);
          });  
        }
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


    // Check Input
    if ( form.camName.value && form.rtspAddress.value)
    {
      var camArray = [...this.state.cameras];
      var sameKey = camArray.find(x => x.name === form.camName.value);
      var sameIp = camArray.find(x => x.rtspAddress === form.rtspAddress.value);
      if (sameKey || sameIp)
      {
        return;
      }

      // Get the existing cameras
      camArray.push({
        name: form.camName.value,
        rtspAddress: form.rtspAddress.value
      });

      // Save the camera to the state
      this.setState({ cameras: camArray }, () => {
        
        // Write the cameras to file for permanent storage
        axios
        .post(path+'/viewing/save-camera', {
          cameras: camArray
        })
        .then(response => {
          console.log("Cameras saved"); 
        })
        .catch(rejected => {
          console.log(`Save Camera Settings rejected: ${rejected}`);
        });
      });
    }
  }

  /**
   * Send the new rtsp stream to the server
   */
  onSelectCamera = (e) => {
    this.setState({ selectedCamIp: e.target.value});
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
      currentCamIp: rtspUrl,
      selectedCamIp: rtspUrl
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
  onSaveCameraSetting = () => {

    if( this.state.currentCamIp !== this.state.selectedCamIp )
    {
      console.log(`Changing Camera: ${this.state.currentCamIp} => ${this.state.selectedCamIp}`);
      this.setState({
        currentCamIp: this.state.selectedCamIp
      }, () => {
        this.state.socket.emit('change-camera', this.state.selectedCamIp);
      });
    }
  }

  getPageInitSetting = () =>{
    // Create data and metadata folders
    axios.post(path+'/viewing/set-up');

    // Get the cameras
    axios
    .post(path+'/viewing/get-cameras')
    .then(response => {
        if (response.data !== "")
        {
          this.setState({
            cameras: response.data
          });
        }
    })
    .catch(rejected => {
      console.log(`Viewing::GetCameras::rejected`);
      console.log(rejected);
    });

    // Get the names of all files already saved
    axios
    .post(path+'/viewing/filenames')
    .then(response => {
      if (response.data !== "")
      {
        this.setState({ 
          filenames: response.data
        });
      }
    })
    .catch(rejected => {
      console.log(`Viewing::GetFilenames::rejected`);
      console.log(rejected);
    });
  }

  render() {
    const {message, mediaSource, isVideoStreaming, saveMessage, currentCamIp} = this.state;

    return (
      <AppWithSideBar listElements={this.sidebarOptions} >
        {/* Live stream and Captured Image */}
        <div className="view-container">
          <h1>Capture</h1>
          
          {/* Change Camera and Capture Image options */}
          <div className="capture-container">
            <AddCamera 
              listElements={this.state.cameras}
              handleSelect={this.onSelectCamera}
              handleAddCam={this.onAddCamera}
              handleSave={this.onSaveCameraSetting}
              currentCamIp={this.state.currentCamIp}
              selectedCamIp={this.state.selectedCamIp}
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

          {/* Live stream */}
          <div className="video-container">
            <canvas ref="captureCanvas" className="capture-canvas" width={880} height={580} hidden={(isVideoStreaming) ? 'hidden' : ''}/>
            <video ref='vidRef' key={mediaSource} hidden={(isVideoStreaming) ? '' : 'hidden'} controls autoPlay playsInline={true} muted="muted">
              <source src={mediaSource}/>
            </video>

            <h3>{message}{(isVideoStreaming) && currentCamIp}</h3>
          </div>
        </div>
      </AppWithSideBar>
    );
  }
}

export default ViewingPage;
