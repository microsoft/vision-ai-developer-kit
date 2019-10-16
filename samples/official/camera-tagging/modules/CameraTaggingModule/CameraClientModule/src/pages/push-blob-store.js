import React, { Component } from 'react';
import axios from 'axios';
import '../styles/push-blob-store.css';
import AppWithSideBar from "../components/sidebar"

const server_port = (process.env.REACT_APP_SERVER_PORT) ? process.env.REACT_APP_SERVER_PORT : '3003';
const path = `http://${document.location.hostname}:${server_port}`;

const local_storage_module_name = process.env.REACT_APP_LOCAL_STORAGE_MODULE_NAME;
const local_storage_port = process.env.REACT_APP_LOCAL_STORAGE_PORT;
const local_storage_account_name = process.env.REACT_APP_LOCAL_STORAGE_ACCOUNT_NAME;
const local_storage_account_key = process.env.REACT_APP_LOCAL_STORAGE_ACCOUNT_KEY;

/**
 * This is the page from which you can push
 * the tagged images to Azure Blob Store.
 */
class PushBlobStorePage extends Component {

    constructor(props) {
        super(props)
        this.state = {
            message: '',
            hasConnectionString: false,
            connectionString: '',
            containers: [],
            chooseNewContainer: false,
            containerName: null,
            hasLocalStorage: true
        }
    }

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

    UNSAFE_componentWillMount () {
        // Check if local storage environment variables set
        if(!local_storage_account_key || !local_storage_account_name || !local_storage_port || !local_storage_module_name) {
            this.setState({
                hasLocalStorage: false
            });
        }
    }

    /**
     * Save the connection string and get associated containers
     */
    onSaveConnectionString = (e) => {
        // Keep the form from switching pages
        e.preventDefault();

        var connectionString = e.target.connectionString.value;

        // Save connection string to state
        this.setState({
            connectionString: connectionString
        });

        axios
        .post(path+'/push-blob-store/get-containers',
        {
            connectionString: connectionString
        })
        .then(response => {
            this.setState({
                containers: response.data,
                message: '',
                hasConnectionString: true
            });
        })
        .catch(rejected => {
            console.log(rejected);
            this.setState({
                message: 'Invalid Connection String'
            });
        })
    }

    /**
     * Save the chosen container name
     */
    handleSelectContainer = (e) => {
        var containerName = e.target.value;
        
        this.setState({
            containerName: containerName
        });
    }

    /**
     * Display field to receive container name.
     */
    handleCreateNewContainer = () => {
        this.setState({
            chooseNewContainer: true
        });
    }

    /**
     * Push the images to the blob store of the appropriate connection string
     */
    handlePushBlobStore = (e) => {
        const { connectionString, chooseNewContainer } = this.state;

        // Keep the form from switching pages
        e.preventDefault();

        // Get the container name
        var containerName = null;
        if(chooseNewContainer) {
            containerName = e.target.containerName.value;
        }
        else {
            containerName = this.state.containerName;
        }

        axios
        .post(path+'/push-blob-store/push',
        {
            connectionString: connectionString,
            containerName: containerName
        })
        .then(response => {
            this.setState({
                message: response.data
            });
        })
        .catch(rejected => {
            console.log(rejected.response);
            this.setState({
                message: 'Failed to push to blob store.'
            });
        });
    }

    /**
     * Creates a connection string to local storage using environment variables.
     * Pushes the images to local block blob store.
     */
    handlePushLocalStore = () => {
        console.log("Push to Local Store");

        var connectionString = `DefaultEndpointsProtocol=http;BlobEndpoint=http://${local_storage_module_name}:${local_storage_port}/${local_storage_account_name};AccountName=${local_storage_account_name};AccountKey=${local_storage_account_key}`;
        var containerName = local_storage_account_name;

        axios
        .post(path+'/push-blob-store/push',
        {
            connectionString: connectionString,
            containerName: containerName
        })
        .then(response => {
            this.setState({
                message: response.data
            });
        })
        .catch(rejected => {
            console.log(rejected.response);
            this.setState({
                message: 'Failed to push to local store.'
            });
        });
    }

    /**
     * Hide the push to local storage option
     */
    handleClickBlobStore = () => {
        this.setState({
            hasLocalStorage: false
        });
    }

    render() {
        const { hasConnectionString, containers, chooseNewContainer, message, hasLocalStorage } = this.state;

        return (
            <AppWithSideBar listElements={this.sidebarOptions} >
                <div className="blob-store-container">
                    <h1>Blob Storage Options</h1>
                    {(hasLocalStorage) && (
                        <div className="blob-buttons-container">
                            <button className="blob-form-button" onClick={this.handlePushLocalStore}>Push to Local Storage</button><br/>
                            <button className="blob-form-button" onClick={this.handleClickBlobStore}>Push to Blob Storage</button>
                        </div>
                    )}

                    {(!hasLocalStorage) && (
                        <div className="blob-form-container">
                            {/* Get the connection string */}
                            <form id="blobForm" method="post" onSubmit={this.onSaveConnectionString}>
                                <label className="blob-form-label" key="endpoint">
                                    {"Storage Connection String"}
                                    <input type="text" className="blob-form-text" name="connectionString" id="connectionString" placeholder="Storage Connection String..."/>
                                </label>
                                <input className="blob-form-button" type="submit" value="Next" hidden={hasConnectionString}/>
                            </form>

                            {/* Get the container name */}
                            <form id="blobForm" method="post" onSubmit={this.handlePushBlobStore} hidden={!hasConnectionString}>
                                <label className="blob-form-label" key="containerName">
                                    {"Container Name"}
                                </label>
                                
                                {/* Existing Containers */}
                                <select className="blob-form-select" defaultValue={'Select Container'} onChange={this.handleSelectContainer} hidden={chooseNewContainer}>
                                    <option value="Select Container" hidden disabled >Select Container</option> 
                                    {containers.map((container) => (
                                        <option key={container} value={container}>{container}</option>
                                    ))}
                                </select><br/>

                                {/* New Container */}
                                <input type="button" className="blob-form-new-container-button" value="Create New Container..." hidden={chooseNewContainer} onClick={this.handleCreateNewContainer}/><br/>
                                <input type="text" className="blob-form-text" name="containerName" id="containerName" placeholder="Container Name..." hidden={!chooseNewContainer}/>
                                <input type="submit" className="blob-form-button" value="Push to Blob Store"/>
                            </form>
                        </div>
                    )}
                    <h3>{message}</h3>
                </div>
            </AppWithSideBar>
        );
    }

}

export default PushBlobStorePage;