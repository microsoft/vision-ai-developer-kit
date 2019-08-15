const fs = require('fs');

module.exports = (app) => {

    const dataRoot = 'CustomVision/data'

    /**
     * Get all the existing tags (folderNames)
     */
    app.post('/review/get-tags', async(req, res) => {
        var tags = [];

        try {
            console.log("Retrieve all existing tags...");

            // Loop through each folder in the directory
            fs.readdirSync(dataRoot).forEach(folderName => {
                tags.push(folderName);
            });
            return res.status(200).send(tags);
        } catch (e) {
            console.log(e);
            return res.status(500).send({
                error: 'Failed to retrieve tags',
                code: 500,
            });
        }
    });

    /**
     * Delete a specific image in a specific folder
     */
    app.post('/review/delete-image/', async(req, res) => {
        const {
            folderName,
            fileName
        } = req.body;

        try {
            console.log(`Delete image ${fileName} from folder ${folderName}`);

            // Delete the image
            fs.unlinkSync(dataRoot+'/'+folderName+'/'+fileName);

            var numFiles = 0;

            // If the folder is now empty, delete the folder
            fs.readdirSync(dataRoot+'/'+folderName).forEach(file => {
                numFiles += 1;
            });
            
            if(numFiles === 0) {
                console.log(`${folderName} is empty. Deleting folder.`);
                fs.rmdirSync(dataRoot+'/'+folderName);
            }

            return res.status(200).send('Successfully deleted file');

        } catch (e) {
            console.log(e);

            return res.status(500).send({
                error: 'Failed to delete image',
                code: 500,
            });
        }
    });

    /**
     * Return a map of {filename: foldernames} which is equivalent to {filename: tag names}
     */
    app.post('/review/image-to-tag-map/', async(req, res) => {

        console.log("Obtain image to tag map");

        var imageToTag = {};

        try {
            // Loop through each folder in the directory
            fs.readdirSync(dataRoot).forEach(folderName => {

                // Loop through each file in the folder
                fs.readdirSync(dataRoot+'/'+folderName+'/').forEach(fileName => {
                    
                    // Add {filename: foldername(tag)} to map
                    if(fileName in imageToTag) {
                        imageToTag[fileName].push(folderName);
                    }
                    else {
                        imageToTag[fileName] = [folderName];
                    }
                    
                });
            });
            return res.status(200).send(imageToTag);

        } catch (e) {
            console.log(e);

            return res.status(500).send({
                error: 'Failed to return image to tag map',
                code: 500,
            });
        }
    });

    /**
     * Obtain all images in the dataRoot as a {filename: image} map which is equivalent to {tagname: image}
     */
    app.post('/review/all-images/', async(req, res) => {

        var nameToImage = {};

        try {
            // Loop through each folder in the directory
            fs.readdirSync(dataRoot).forEach(folderName => {

                // Loop through each file in the folder
                fs.readdirSync(dataRoot+'/'+folderName+'/').forEach(fileName => {

                    // Get the image
                    var image = fs.readFileSync(dataRoot+'/'+folderName+'/'+fileName, 'base64');
                    
                    // Add {filename: image} to map
                    if(!(fileName in nameToImage)) {
                        nameToImage[fileName] = image;
                    }
                    
                });
            });

            return res.status(200).send(nameToImage);

        } catch (e) {
            console.log(e);
            return res.status(500).send({
                error: 'Failed to return image to tag map',
                code: 500,
            });
        }
    });

    /**
     * Saves the image with a new tag (in a new folder)
     */
    app.post('/review/add-tag/', async(req, res) => {
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
            console.log(`Saving image ${imageName} with tag ${tag}`);
            // Create the folder
            fs.mkdir(dataRoot+'/'+tag, { recursive: true }, (err) => {
                if (err) {
                    console.log(err);
                }
                else {
                    console.log(`${tag} directory created successfully`);
                }
            });

            // Save the image
            var imageData = image.replace(/^data:image\/\w+;base64,/,"");
            var buf = new Buffer.from(imageData, 'base64');
            fs.writeFile(dataRoot+'/'+tag+'/'+imageName, buf, (err) => {
                if (err) {
                    console.log(err);
                }
                else {
                    console.log(`${imageName} saved successfully in ${tag}`);
                }
            });
            return res.status(200).send("Image successfully saved");
        } catch (e) {
            return res.status(500).send({
                error: 'Failed to save image',
                code: 500,
            });
        }
    });
};