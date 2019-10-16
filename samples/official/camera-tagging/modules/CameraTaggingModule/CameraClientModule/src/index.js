import React from 'react';
import ReactDOM from 'react-dom';
import ViewingPage from './pages/viewing';
import ReviewPage from './pages/review';
import UploadPage from './pages/upload'; 
import PushCustomVisionPage from './pages/push-custom-vision';
import PushBlobStorePage from './pages/push-blob-store';
import { Route, BrowserRouter as Router } from 'react-router-dom';
import * as serviceWorker from './serviceWorker';
import './styles/index.css'
require('dotenv').config();

const routing = (
    <Router>
        <Route exact path="/" component={ViewingPage} />
        <Route path="/review" component={ReviewPage} />
        <Route path="/upload" component={UploadPage} />
        <Route path="/push-custom-vision" component={PushCustomVisionPage} />
        <Route path="/push-blob-store" component={PushBlobStorePage} />
    </Router>
);

ReactDOM.render(routing, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
