const fs = require('fs');

const dataRoot = 'CustomVision/data';

const azure = require('azure-storage');

module.exports = (app) => {

  /**
   * Get all the container names associated with the connection string.
   */
  app.post('/push-blob-store/get-containers/', async (req, res) => {
    const {
      connectionString
    } = req.body;

    try {
      console.log(`Obtain container names associated with connection string: ${connectionString}...`);
      
      const blobService = azure.createBlobService(connectionString);
      var containers = [];

      // Get all containers associated with this storage account
      blobService.listContainersSegmented(null, (error, result) => {
        // Get names of containers
        for(var index in result.entries) {
          containers.push(result.entries[index].name);
        }

        return res.status(200).send(containers);
      });

    } catch (e) {
        console.log(e);
        return res.status(500).send({
          error: e,
          code: 500,
        });
    }
  });

  /**
   * Push images to blob store
   * The container is specified on the client side.
   * Each tag becomes its own folder in the blob store.
   */
  app.post('/push-blob-store/push/', async (req, res) => {
    const {
      connectionString,
      containerName
    } = req.body;

    try {
      const blobService = azure.createBlobService(connectionString);

      blobService.createContainerIfNotExists(containerName, { publicAccessLevel: 'blob' }, error => {

        // Create a folder in the container per tag
        const tagFolders = fs.readdirSync(dataRoot);
        for (const folder of tagFolders) {

          console.log("Adding images for tag: " + folder);

          // Upload each image in the folder to Blob store
          const taggedImages = fs.readdirSync(dataRoot + '/' + folder);
          taggedImages.forEach(fileName => {
            console.log("Adding Image...." + folder + '/' + fileName);
            blobService.createBlockBlobFromLocalFile(
              containerName,
              folder + '/' + fileName,
              dataRoot + '/' + folder + '/' + fileName,
              (error, result) => {
                if (error) return res.status(500).send(error);
                console.dir(result, { depth: null, colors: true });
              }
            );
          });
        }
      });

      return res.status(200).send("Success");

    } catch (e) {
      console.log(e);
      return res.status(500).send({
        error: e,
        code: 500,
      });
    }
  });

};