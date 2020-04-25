import React, { Component } from 'react';
import axios from 'axios';
import AppWithSideBar from "../components/sidebar"
import '../styles/push-custom-vision.css';

const server_port = (process.env.REACT_APP_SERVER_PORT) ? process.env.REACT_APP_SERVER_PORT : '3003';
const path = `http://${document.location.hostname}:${server_port}`;

/**
 * This is the page from which you can push
 * the tagged images to Custom Vision in
 * order to train the ML model.
 */
class PushCustomVisionPage extends Component {

    constructor(props) {
        super(props)
        this.state = {
            message: '',
            hasTrainingKey: false,
            isTraining: false,
            projectNames: [],
            chooseNewProject: false,
            projectName: null,
            trainingKey: '',
            endpoint: '',
            projectDomains: [],
            selectedProjDomain: null
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

    /**
     * Saves the training key and gets project names associated with it.
     */
    onSaveKeyAndEndpoint = (e) => {
        // Keep the form from switching pages
        e.preventDefault();

        // Get and save the training key and endpoint
        var trainingKey = e.target.trainingKey.value;
        var endpoint = e.target.endpoint.value;

        this.setState({
            trainingKey: trainingKey,
            endpoint: endpoint
        });

        // Get projects for this training key
        axios
        .post(path+'/push-custom-vision/get-projects',
        {
            trainingKey: trainingKey,
            endpoint: endpoint
        })
        .then(response => {
            this.setState({ 
                projectNames: response.data,
                hasTrainingKey: true,
                message: ''
            });
        })
        .catch(rejected => {
            console.log(rejected);
            this.setState({
                message:'Invalid Inputs'
            })
        });
    }

    /**
     * Sends images to custom vision and trains model
     */
    pushToCustomVision = (e) => {
        const { chooseNewProject, trainingKey, selectedProjDomain, endpoint } = this.state;

        // Keep the form from switching pages
        e.preventDefault();

        // Get the project name
        var projectName = null;
        if(chooseNewProject) {
            // New project name
            projectName = e.target.projectName.value

            // Make sure a domain is selected for this new project
            if(!selectedProjDomain) {
                this.setState({
                    message: 'Must select a domain.'
                });
                return;
            }
        } 
        else {
            // Existing project
            projectName = this.state.projectName;
        }

        this.setState({
            isTraining: true,
            message: ''
        });

        axios
        .post(path+'/push-custom-vision/push',
        {
            trainingKey: trainingKey,
            endpoint: endpoint,
            projectName: projectName,
            projectDomain: selectedProjDomain
        })
        .then(response => {
            this.setState({ 
                message: response.data,
                isTraining: false
            });
        })
        .catch(rejected => {
            console.log(rejected.response);

            this.setState({
                message: 'Could not push to Custom Vision.',
                isTraining: false
            });
        })
    }

    /**
     * Save the existing project that is selected.
     */
    handleSelectProj = (e) => {
        var projectName = e.target.value;

        this.setState({
            projectName: projectName
        });
    }

    /**
     * Save the project domain when it is selected.
     */
    handleSelectProjDomain = (e) => {
        var selectedProjDomain = e.target.value;

        this.setState({
            selectedProjDomain: selectedProjDomain
        });
    }

    /**
     * Get all possible project domains from the endpoint.
     */
    handleCreateNewProject = () => {
        const { trainingKey, endpoint } = this.state;

        this.setState({
            chooseNewProject: true
        });

        // Get the project domains
        axios
        .get(`${endpoint}/customvision/v3.0/training/domains?Training-Key=${trainingKey}`)
        .then(response => {
            this.setState({
                projectDomains: response.data
            });
        })
        .catch(rejected => {
            console.log(rejected);
        });
    }

    render() {
        const { message, isTraining, projectNames, hasTrainingKey, chooseNewProject, projectDomains } = this.state;

        return (
            <AppWithSideBar listElements={this.sidebarOptions} >
                <div className="push-container">
                    <div className="form-container">
                        <h1>Custom Vision API Settings</h1>
                        {/* Get the endpoint and training key */}
                        <form id="pushForm" method="post" onSubmit={this.onSaveKeyAndEndpoint}>
                            <label className="push-form-label" key="endpoint">
                                {"Endpoint"}
                                <input type="text" className="push-form-text" name="endpoint" id="endpoint" placeholder="Endpoint..."/>
                            </label>
                            <label className="push-form-label" key="trainingKey">
                                {"Training Key"}
                                <input type="text" className="push-form-text" name="trainingKey" id="trainingKey" placeholder="Training Key..."/>
                            </label>
                            <input className="push-form-button" type="submit" value="Next" hidden={hasTrainingKey}/>
                        </form>

                        {/* Get project name */}
                        <form id="pushForm" method="post" onSubmit={this.pushToCustomVision} hidden={!hasTrainingKey}>
                            <label className="push-form-label" key="projectName">
                                {"Project Name"}
                            </label>
                            
                            {/* Existing Projects */}
                            <select className="push-form-select" defaultValue={'Select Project'} onChange={this.handleSelectProj} hidden={chooseNewProject}>
                                <option value="Select Project" hidden disabled >Select Project</option> 
                                {projectNames.map((projName) => (
                                    <option key={projName} value={projName}>{projName}</option>
                                ))}
                            </select><br/>

                            {/* New Project */}
                            <input type="button" className="push-form-new-project-button" value="Create New Project..." hidden={chooseNewProject} onClick={this.handleCreateNewProject}/><br/>
                            <input type="text" name="projectName" id="projectName" placeholder="Project Name..." hidden={!chooseNewProject}/>
                            {/* Project Domains */}
                            <select className="push-form-select" defaultValue={'Select Domain'} onChange={this.handleSelectProjDomain} hidden={!chooseNewProject}>
                                <option value="Select Domain" hidden disabled >Select Domain</option> 
                                {projectDomains.map((projDomain) => (
                                    <option key={projDomain.name+projDomain.type} value={projDomain.id}>{projDomain.name} - {projDomain.type}</option>
                                ))}
                            </select><br/>
                            <input type="submit" className="push-form-button" value="Push to Custom Vision"/>
                        </form>

                        {isTraining && (<div className='push-training'>Uploading</div>)}
                        <h3>{message}</h3>
                    </div>
                </div>
            </AppWithSideBar>
        );
    }

}

export default PushCustomVisionPage;