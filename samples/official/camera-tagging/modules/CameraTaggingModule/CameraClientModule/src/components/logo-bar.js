import React, { Component } from 'react';
import microsoftLogo from '../static/microsoft-logo.png';
import '../styles/logo-bar.css'


class LogoBar extends Component {
    render() {
        return (
            <div className="logo-bar">
                <img alt='Microsoft' src={microsoftLogo} className="microsoftLogo" />
            </div>
        );
    }
}

export default LogoBar;