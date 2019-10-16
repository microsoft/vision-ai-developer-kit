import React, { Component } from 'react';
import AppWithSideBar from "../components/sidebar"
import '../styles/upload.css';

/**
 * This is the page from which you can push
 * the tagged images to Custom Vision in
 * order to train the ML model.
 */
class UploadPage extends Component {

    /* eslint-disable no-useless-constructor */
    constructor(props) {
        super(props);
        this.toCustomVision = this.toCustomVision.bind(this);
        this.toBlobStorage = this.toBlobStorage.bind(this);
    }
    /* eslint-enable no-useless-constructor */

    sidebarOptions = [
        {
          name: 'Capture',
          handleClick: () => this.props.history.push('/'),
          children: []
        },
        {
          name: 'Images',
          handleClick: () => this.props.history.push('/review'),
          children: []
        },
        {
          name: 'Upload Settings',
          handleClick: () => this.props.history.push('/upload'),
          children: [],
          isActive: true
        }
    ];

    toCustomVision() {
        this.props.history.push('/push-custom-vision');
    }

    toBlobStorage() {
        this.props.history.push('/push-blob-store');
    }

    render() {
        return (
            <AppWithSideBar listElements={this.sidebarOptions} >
               <div  className="upload-container">
                <h1>Upload Settings</h1>
                <p>Tell us where to store your images.</p>
                <button onClick={this.toCustomVision} className="upload-option-button">Custom Vision</button>
                <button onClick={this.toBlobStorage} className="upload-option-button">Blob Storage</button>
               </div>
            </AppWithSideBar>
        );
    }

}

export default UploadPage;