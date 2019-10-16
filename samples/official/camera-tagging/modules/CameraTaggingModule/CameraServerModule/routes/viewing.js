const fs = require('fs');

module.exports = (app) => {

    const dataRoot = 'CustomVision/data'
    const metadataRoot = 'CustomVision/metadata'

    /**
     * Initialize the data and metadata folders
     */
    app.post('/viewing/set-up', async(req, res) => {
        console.log('Creating directories');
        try {

            // Make the data folder
            fs.mkdir(dataRoot, { recursive: true }, (err) => {
                if (err) {
                    console.error(`Failed to create ${dataRoot} directory created. Error:${err}`);
                }
            });

            // Make the metadata folder
            fs.mkdir(metadataRoot, { recursive: true }, (err) => {
                if (err) {
                    console.error(`Failed to create ${metadataRoot} directory created. Error:${err}`);
                }
            });

            return res.status(201).send('directories created');

        } catch (e) {
            console.error(e);

            return res.status(500).send({
                error: 'Failed to create initial directories',
                code: 500,
            });
        }
    });

    /**
     * Save the captured image in a folder with its tag name
     */
    app.post('/viewing/capture/', async(req, res) => {
        const {
            image, tag, imageName,
        } = req.body;

        // Ensure all data is received
        if(!tag) {
            return res.status(400).json({
                error: 'Please enter a tag name',
                code: 400,
            });
        }
        else if(!imageName) {
            return res.status(400).send({
                error: 'Please enter an image name',
                code: 400,
            });
        }

        try {
            console.log(`Saving ${imageName} to folder ${tag}.`);

            // Create the folder
            fs.mkdirSync(dataRoot+'/'+tag, { recursive: true }, (err) => {
                if (err) {
                    console.log(err);
                }
                else {
                    console.log(`${tag} directory created successfully.`);
                }
            });

            // Save the image
            var imageData = image.replace(/^data:image\/\w+;base64,/,"");
            var buf = new Buffer.from(imageData, 'base64');
            fs.writeFileSync(dataRoot+'/'+tag+'/'+imageName+".png", buf, (err) => {
                if (err) {
                    console.log(err);
                }
                else {
                    console.log(`${imageName} successfully saved to ${tag}.`);
                }
            });

            return res.status(200).send("Image successfully saved");

        } catch (e) {
            console.log(e);

            return res.status(500).send({
                error: 'Failed to save image',
                code: 500,
            });
        }
    });

    /**
     * Get all of the image filenames in every folder
     */
    app.post('/viewing/filenames/', async(req, res) => {

        console.log("Get all the filenames from every folder...");
        var filenames = [];

        try {

            if (!fs.existsSync(metadataRoot+'/'+'cameras.json'))
            {
                return res.status(204).send(null);
            }

            // Loop through each folder in the directory
            fs.readdirSync(dataRoot).forEach(folderName => {

                // Loop through each file in the folder
                fs.readdirSync(dataRoot+'/'+folderName+'/').forEach(fileName => {
                    
                    // Add filename to filenames
                    if(!(filenames.includes(fileName))) {
                        filenames.push(fileName);
                    }
                });
            });

            return res.status(200).send(filenames);

        } catch (e) {
            console.log(e);
            return res.status(500).send({
                error: 'Failed to return filenames',
                code: 500,
            });
        }
    });

    /**
     * Save any new camera metadata to file
     */
    app.post('/viewing/save-camera', async(req, res) => {
        const {
            cameras
        } = req.body;

        console.log("Saving cameras.");
        console.log(`save-camera::json:: ${cameras}`);

        try {
            var jsonCam = JSON.stringify(cameras);

            // Write cameras JSON to file
            fs.writeFile(metadataRoot+'/'+'cameras.json', jsonCam, 'utf8', (err) => {
                if (err) {
                    console.log(err);
                }
                else {
                    console.log("cameras.json file created successfully");
                }
            });
        } catch (e) {
            console.log(e);

            return res.status(500).send({
                error: 'Failed to save camera data',
                code: 500
            });
        }
        
    });

    /**
     * Get all of the camera metadata
     */
    app.post('/viewing/get-cameras', async(req, res) => {

        console.log("Get all camera metadata.");
        var cameras;

        try {
            // Get cameras from JSON file
            if (!fs.existsSync(metadataRoot+'/'+'cameras.json'))
            {
                return res.status(204).send(null);
            }

            var cameras = fs.readFileSync(metadataRoot+'/'+'cameras.json', 'utf8');
            camerasObj = JSON.parse(cameras);
            return res.status(200).send(camerasObj);

        } catch (e) {
            console.log(e);           
            return res.status(500).send({
                error: 'Failed to get camera data',
                code: 500
            });
        }
        
    });
};