const fs = require('fs');
const util = require('util');

const TrainingApiClient = require("@azure/cognitiveservices-customvision-training");

const setTimeoutPromise = util.promisify(setTimeout);

const dataRoot = 'CustomVision/data';

// To export the model to Vision AI Dev Kit
const targetExportPlatform = 'VAIDK';

module.exports = (app) => {

    /**
     * Get all the existing projects associated with the training key.
     */
    app.post('/push-custom-vision/get-projects/', async(req, res) => {
        const {
            trainingKey,
            endpoint
        } = req.body;
        
        // Ensure all data is received
        if(!trainingKey) {
            return res.status(400).send({
                error: 'Please enter your training key',
                code: 400,
            });
        }

        if(!endpoint) {
            return res.status(400).send({
                error: 'Please enter your endpoint',
                code: 400,
            });
        }

        try {
            console.log(`Get all existing projects associated with training key: ${trainingKey}...`);

            const trainer = new TrainingApiClient.TrainingAPIClient(trainingKey, endpoint);

            // Get all projects
            const projects = await trainer.getProjects();

            var projectNames = [];

            // Push project names to array
            for(var index in projects) {
                projectNames.push(projects[index].name);
            }

            return res.status(200).send(projectNames);

        } catch (e) {
            console.log(e);
            return res.status(500).send({
                error: e,
                code: 500,
            });
        }
    });

    /**
     * Push all images to the specified Custom Vision Project
     */
    app.post('/push-custom-vision/push/', async(req, res) => {
        const {
            trainingKey,
            endpoint,
            projectName,
            projectDomain
        } = req.body;

        // Ensure all data is received
        if(!projectName) {
            return res.status(400).send({
                error: 'Please enter a project name',
                code: 400,
            });
        }

        try {
            const trainer = new TrainingApiClient.TrainingAPIClient(trainingKey, endpoint);

            const projects = await trainer.getProjects();

            var project = null;
            var tags = null;
            var projectExists = false;

            // If the project already exists, just update it
            for(var index in projects) {
                if(projects[index].name === projectName) {
                    projectExists = true;
                    project = projects[index];

                    // Get tags of the project
                    tags = await trainer.getTags(project.id);
                }
            }

            // Else, create a new project
            if(!projectExists) {
                console.log("Creating project...");
                project = await trainer.createProject(projectName, {domainId: projectDomain, targetExportPlatforms: [targetExportPlatform]});
            }

            let fileUploadPromises = [];

            // Create a tag per folder in the data root directory
            const tagFolders = fs.readdirSync(dataRoot);
            for (const folder of tagFolders) {
                var imageTag = null;

                // If the project and tag already exists, use that tag
                if(projectExists) {
                    for(var index in tags) {
                        if(tags[index].name === folder) {
                            imageTag = tags[index];
                        }
                    }
                }

                // Else, create a new tag
                if (!imageTag) {
                    console.log(`Creating tag: ${folder}`);
                    imageTag = await trainer.createTag(project.id, folder);
                }

                console.log(`Adding images for tag: ${folder}`);

                // Upload each image in the folder to Custom Vision
                const taggedImages = fs.readdirSync(dataRoot+'/'+folder);
                taggedImages.forEach(file => {
                    console.log("Adding Image...."+folder+'/'+file);
                    fileUploadPromises.push(trainer.createImagesFromData(project.id, fs.readFileSync(dataRoot+'/'+folder+'/'+file), { tagIds: [imageTag.id] }));
                })
            }
            // Wait for all files to upload
            await Promise.all(fileUploadPromises);

            return res.status(200).send("Success");

        } catch (e) {

            console.log(e);
            
            return res.status(500).send({
                error: e,
                code: 500,
            });
        }
    });

    /**
     * train Custom Vision Project
     */
    app.post('/push-custom-vision/train/', async(req, res) => {
        const {
            trainingKey,
            endpoint,
            projectName
        } = req.body;

        // Ensure all data is received
        if(!projectName) {
            return res.status(400).send({
                error: 'Please enter a project name',
                code: 400,
            });
        }

        try {
            const trainer = new TrainingApiClient.TrainingAPIClient(trainingKey, endpoint);
            const projects = await trainer.getProjects();
            var project = null;

            // If the project already exists, just update it
            for(var index in projects) {
                if(projects[index].name === projectName) {
                    projectExists = true;
                    project = projects[index];
                }
            }

            if(projectExists)
            {
                console.log("Training...");
                let trainingIteration = await trainer.trainProject(project.id);
    
                // Wait for training to complete
                console.log("Training started...");
                while (trainingIteration.status == "Training") {
                    console.log("Training status: " + trainingIteration.status);
                    await setTimeoutPromise(1000, null);
                    trainingIteration = await trainer.getIteration(project.id, trainingIteration.id)
                }
                console.log("Training status: " + trainingIteration.status);
    
                return res.status(200).send("Success");
            }
            else
            {
                return res.status(400).send(`Cannot find project with name - ${projectName}.`);
            }

        } catch (e) {

            console.log(e);
            
            return res.status(500).send({
                error: e,
                code: 500,
            });
        }
    });
};