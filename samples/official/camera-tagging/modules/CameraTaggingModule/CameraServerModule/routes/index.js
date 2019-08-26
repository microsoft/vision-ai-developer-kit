module.exports = (app) => {

  // Load app into the other routes
  const viewingRoute = require('./viewing');
  viewingRoute(app);

  const reviewRoute = require('./review');
  reviewRoute(app);

  const pushCustomVisionRoute = require('./push-custom-vision');
  pushCustomVisionRoute(app);

  const pushBlobStoreRoute = require('./push-blob-store');
  pushBlobStoreRoute(app);
};
