import React from 'react';
import PropTypes from 'prop-types';
import Popup from 'reactjs-popup';
import '../styles/add-camera.css'

const popupContentStyle = {
  maxWidth: "500px",
  width: "30%",
  height: "auto",
  borderRadius: "30px",
  borderColor: "#254069",
  borderWidth: "3px"
};

const AddCameraProps = {
  listElements: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      rtspAddress: PropTypes.string
    })
  ),
  handleSelect: PropTypes.func.isRequired,
  handleAddCam: PropTypes.func.isRequired,
  handleSave: PropTypes.func.isRequired,
  currentCamIp: PropTypes.string.isRequired
};

/**
 * This component contains everything required to
 * change the rtsp stream. It allows to pick from
 * streams already saved, or enter a new camera name
 * and associated rtsp stream.
 */
export const AddCamera = ({ listElements = [], handleSelect, handleAddCam, handleSave, currentCamIp, selectedCamIp }) => {
  return (
    <Popup className="add-cam-popup" 
            contentStyle={popupContentStyle} 
            trigger={<button className="change-cam-btn">Change Camera</button>} 
            modal>
      {close => (
        <div className="modal">
          <div className="header">
            Change Camera
          </div>

          {/* Dropdown to select which rtsp stream to view */}
          <div className="change-cam-content">
            <select className="camera-list" id="camera-list" defaultValue={currentCamIp} onChange={handleSelect}>
              <option value="Select Camera" hidden disabled >Select Camera</option>
              {listElements.map(
                ({ name, rtspAddress }, index) => (
                  <option title={rtspAddress} key={index} value={rtspAddress}>{name} - {rtspAddress}</option>
                )
              )}
            </select><br/>
            <h4 className="select-camera-label">Selected: {selectedCamIp}</h4>
          </div>

          {/* Section to add a new camera name and associated rtsp stream */}
          <div className="add-cam-content">
            To add a new camera, enter the RTSP address in the form "rtsp://x.x.x.x:PORT/PATH"
            <form className="add-cam-form" id="add-cam-form" onSubmit={(e) => handleAddCam(document.getElementById("add-cam-form"), e)}>
              <input className="add-cam-input" name="camName" type="text" placeholder="Camera Name..." onInput={()=>{}}/><br/>
              <input className="add-cam-input" name="rtspAddress" type="text" placeholder="RTSP Address..."/><br/>
              <input className="add-cam-button" name="addCam" type="submit" value="Add Camera" />
            </form>
          </div>

          <div className="actions">
            <button className='popUpButton' onClick={() => { handleSave(); close();}}>Save</button>
            <button className="popUpButton" onClick={() => { close(); }}>Quit</button>
          </div>
        </div>
      )}
    </Popup>
  );
};
  
AddCamera.propTypes = AddCameraProps;

export default AddCamera;