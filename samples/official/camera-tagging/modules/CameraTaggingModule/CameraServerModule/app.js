const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const cors = require('cors');
const fileUpload = require('express-fileupload');
const bodyParser = require('body-parser');
const Mpeg4Stream = require('./scripts/mpeg4-stream');
const withRoutes = require('./routes');
var Transport = require('azure-iot-device-mqtt').Mqtt;
var Client = require('azure-iot-device').ModuleClient;
const fs = require('fs');
const azure = require('azure-storage');
const TrainingApiClient = require("@azure/cognitiveservices-customvision-training");

const dataRoot = 'CustomVision/data'

const app = express();

app.use(logger('dev'));
app.use(bodyParser.json({limit:'50mb'}));
app.use(bodyParser.urlencoded({ extended: true, limit:'50mb' }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use(cors());
app.use(fileUpload());

withRoutes(app);

// catch 404 and forward to error handler
app.use(function(req, res) {//, next
  // next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

/**
 * Normalize a port into a number, string, or false.
 */
function normalizePort(val) {
  var port = parseInt(val, 10);

  if (isNaN(port)) {
    // named pipe
    return val;
  }

  if (port >= 0) {
    // port number
    return port;
  }

  return false;
}

// Read in port from the environment variables if one exists
const wsPort = normalizePort(process.env.WEB_SOCKET_PORT || '3002');

const mpeg4 = new Mpeg4Stream('camera', 3001, wsPort);
mpeg4.startStreamingServer();

// Set up messages from edgeHub
Client.fromEnvironment(Transport, function (err, client) {
  if (err) {
    throw err;
  } else {
    client.on('error', function (err) {
      throw err;
    });

    // connect to the Edge instance
    client.open(function (err) {
      if (err) {
        throw err;
      } else {
        console.log('IoT Hub module client initialized');

        // Act on input messages to the module.
        client.onMethod('capture', captureImage);
        client.onMethod('delete', deleteImages);
        client.onMethod('push', pushToBlobStore);
        client.onMethod('upload', uploadToCustomVision);


      }
    });
  }
});

// Callback on event "capture"
function captureImage(request, response) {
  // Check for proper payload
  var payload = request.payload;

  if(!payload) {
    response.send(500, 'RTSP_IP required');
    return;
  }
  else if(!payload.RTSP_IP) {
    response.send(500, 'RTSP_IP required');
    return;
  }
  else if(!payload.TAGS) {
    response.send(500, 'At least 1 tag required in TAGS');
    return;
  }

  try {
    mpeg4.captureImage(payload);
  }
  catch (e) {
    console.log(e);
    response.send(500, 'Capture Fail');
    return;
  }
  finally {
    response.send(200, 'Capture Success');
  }
}

// Callback on event "delete"
function deleteImages(request, response) {
  try {
    // Delete all folders under dataRoot
    fs.readdirSync(dataRoot).forEach(folderName => {

      // Loop through each file in the folder
      fs.readdirSync(dataRoot+'/'+folderName+'/').forEach(fileName => {   
        // Delete the image
        fs.unlinkSync(dataRoot+'/'+folderName+'/'+fileName);
      });

      // Delete the folder
      fs.rmdirSync(dataRoot+'/'+folderName);
    });

    response.send(200, 'Success');
  } catch (e) {
    console.log(e);
    response.send(500, 'Failed to delete folders');
  }
}

// Callback on event "push"
function pushToBlobStore(request, response) {
  var payload = request.payload;
  
  if(!payload.ACCOUNT_KEY || !payload.ACCOUNT_NAME || !payload.MODULE_NAME || !payload.STORAGE_PORT) {
    response.send(500, 'Need to provide ACCOUNT_KEY, ACCOUNT_NAME, MODULE_NAME, and STORAGE_PORT for local storage');
    return;
  }

  var connectionString = `DefaultEndpointsProtocol=http;BlobEndpoint=http://${payload.MODULE_NAME}:${payload.STORAGE_PORT}/${payload.ACCOUNT_NAME};AccountName=${payload.ACCOUNT_NAME};AccountKey=${payload.ACCOUNT_KEY}`;
  var containerName = payload.ACCOUNT_NAME;
  var deleteImage = payload.DELETE;

  try {
    const blobService = azure.createBlobService(connectionString);

    blobService.createContainerIfNotExists(containerName, { publicAccessLevel: 'blob' }, error => {

      // Create a folder in the container per tag
      fs.readdirSync(dataRoot).forEach(folder => {
        // Upload each image in the folder to Blob store
        fs.readdirSync(dataRoot + '/' + folder).forEach(fileName => {
          blobService.createBlockBlobFromLocalFile(
            containerName,
            folder + '/' + fileName,
            dataRoot + '/' + folder + '/' + fileName,
            (error, result) => {
              if (error) {
                console.log(error);
                return;
              }
              console.dir(result, { depth: null, colors: true });

              // Delete image if the flag is set
              if(deleteImage) {
                // Delete the image
                fs.unlinkSync(dataRoot+'/'+folder+'/'+fileName);

                var numFiles = 0;

                // If the folder is now empty, delete the folder
                fs.readdirSync(dataRoot+'/'+folder).forEach(file => {
                  numFiles += 1;
                });
              
                if(numFiles === 0) {
                  fs.rmdirSync(dataRoot+'/'+folder);
                }
              }
            }
          );
        });
      });
        
    });

  } catch (e) {
    console.log(e);
  }
  response.send(200, 'Success');
}

// Callback on event "upload"
async function uploadToCustomVision(request, response) {
  var payload = request.payload;

  if(!payload.ENDPOINT || !payload.KEY || !payload.PROJECT_ID) {
    response.send(500, 'Need to provide ENDPOINT, KEY, and PROJECT_ID for Custom Vision project');
    return;
  }

  var endpoint = `https://${payload.ENDPOINT}/`;
  var trainingKey = payload.KEY;
  var projectid = payload.PROJECT_ID;

  try {
    const trainer = new TrainingApiClient.TrainingAPIClient(trainingKey, endpoint);

    // Get tags of the project
    projectExists = true;
    tags = await trainer.getTags(projectid);

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
            imageTag = await trainer.createTag(projectid, folder);
        }

        console.log(`Adding images for tag: ${folder}`);

        // Upload each image in the folder to Custom Vision
        const taggedImages = fs.readdirSync(dataRoot+'/'+folder);
        taggedImages.forEach(file => {
            console.log("Adding Image...."+folder+'/'+file);
            fileUploadPromises.push(trainer.createImagesFromData(projectid, fs.readFileSync(dataRoot+'/'+folder+'/'+file), { tagIds: [imageTag.id] }));
        })
    }
    // Wait for all files to upload
    await Promise.all(fileUploadPromises);

  } catch (e) {

    console.log(e);
    
    return res.status(500).send({
        error: e,
        code: 500,
    });
  }
  response.send(200, 'Success');

}


module.exports = app;
