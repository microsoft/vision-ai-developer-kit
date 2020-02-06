import React, { Component } from 'react';
import axios from 'axios';
import AppWithSideBar from '../components/sidebar';
import Popup from 'reactjs-popup';
import DeleteButton from '../static/delete-button.png'
import '../styles/review.css';

const server_port = (process.env.REACT_APP_SERVER_PORT) ? process.env.REACT_APP_SERVER_PORT : '3003';
const path = `http://${document.location.hostname}:${server_port}`;

const popupContentStyle = {
  width: "auto",
  height: "auto",
};

const deletePopupContentStyle = {
  maxWidth: "500px",
  width: "30%",
  height: "auto",
  borderRadius: "30px",
  borderColor: "#254069",
  borderWidth: "3px"
};

/**
 * This is the page from which you can view
 * captured images, delete images, and delete tags.
 */
class ReviewPage extends Component {

  constructor(props) {
    super(props)
    this.state = {
      loaded: false,
      imageToTag: new Map(),
      nameToImage: new Map(),
      isTagSelected: new Map(),
      isImageSelected: new Map(),
      tags: []
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
      children: [],
      isActive: true
    },
    {
      name: 'Upload Settings',
      handleClick: () => this.props.history.push('/upload'),
      children: []
    }
  ];

  /**
   * Get all the images, tags, and the association of image: tag
   */
  UNSAFE_componentWillMount() {
    this.getImages(true);
    this.getImageTagMap();
    this.getTags(true);
  }

  /**
   * Get a map of {imageName: image}
   * If flag resetSelectedImages is true, reset which images are selected.
   */
  getImages = (resetSelectedImages) => {
    // Get a map of {imageName: image}
    axios
      .post(path + '/review/all-images')
      .then(response => {
        this.setState({
          nameToImage: response.data
        });
      })
      .catch(rejected => {
        console.log(rejected);
      })
      .finally(e => {

        if(resetSelectedImages) {
          // Get all filenames
          var isImageSelected = this.state.isImageSelected;
          var fileNames = Object.keys(this.state.nameToImage);

          /* eslint-disable no-unused-vars */
          // Initiate each image to not be selected
          for(var [index, fileName] of fileNames.entries()) {
            isImageSelected[fileName] = false;
          }
          /* eslint-enable no-unused-vars */

          this.setState({
            isImageSelected: isImageSelected
          });
        }
      });
    }

  /**
   * Get a map of {image: tags} 
   * where tags is an array.
   */
  getImageTagMap = () => {
    axios
      .post(path + '/review/image-to-tag-map')
      .then(response => {
        this.setState({
          imageToTag: response.data
        });
      })
      .catch(rejected => {
        console.log(rejected);
      })
      .finally(e => {
        this.setState({
          loaded: true
        });

        // Update which images that are selected based on their tags
        this.updateSelectedImages();
      });
  }

  /**
   * Get all of the tags that have been made.
   * If flag resetSelectedTags is true, reset tags selected.
   */
  getTags = (resetSelectedTags) => {
    axios
      .post(path+'/review/get-tags')
      .then(response => {
        this.setState({
          tags: response.data
        });
      })
      .catch(rejected => {
        console.log(rejected);
      })
      .finally(e => {
        if(resetSelectedTags) {
          // Initiate the tags to not be selected
          var isTagSelected = this.state.isTagSelected;

          /* eslint-disable no-unused-vars */
          for(var [index, tag] of this.state.tags.entries()) {
            isTagSelected[tag] = false;
          }
          /* eslint-enable no-unused-vars */
        }
      });
  }

  /**
   * Renders the table of the captured images.
   * Each image is a trigger for a popup that allows image detail to be edited.
   */
  renderImageTable = () => {
    const { imageToTag, nameToImage, isImageSelected } = this.state;
    var self = this;
    var imgs = [];

    // Get all of the image file names
    var fileNames = Object.keys(nameToImage);

    // Each image leads to a popup where you can edit image details
    imgs.push(fileNames.map(function (fileName, index) {
      return (
        <div className="thumbnails" key={fileName + index}>
          <Popup contentStyle={popupContentStyle}
            trigger={<img className={isImageSelected[fileName] ? "thumbImage-selected" :  "thumbImage"} src={'data:image/png;base64, ' + nameToImage[fileName]} alt={fileName} key={'image' + index} />}
            modal>
            {close => (
              <div className="review-popup-modal">
                <button type="button" onClick={close}>
                  &times;
                </button>

                <div className="review-popup-header">
                  Image Detail
                </div>

                <div className="review-popup-main">
                  <div className="review-popup-image-container">
                    <img className="review-popup-image" src={'data:image/png;base64, ' + nameToImage[fileName]} alt={fileName} key={'image' + index} />
                    <Popup className="delete-Popup"
                      contentStyle={deletePopupContentStyle}
                      trigger={<button className="popUpButton" onClick={() => { close(); }}>Delete Image</button>}
                      modal>
                      {close => (
                        <div className="modal">
                          <div className="content">
                            {" "}
                            Are you sure you want to permanently delete this image?
                                                    </div>
                          <div className="actions">
                            <button className="popUpButton" onClick={() => { close(); }}>No</button>
                            <button className='popUpButton' onClick={() => { self.onClickImageDelete(fileName); close(); }}>Yes</button>
                          </div>
                        </div>
                      )}
                    </Popup>
                  </div>

                  <div className="review-popup-tags-container">
                    <form className="review-popup-tag-form" id="review-popup-tag-form" method="post" onSubmit={(e) => self.onAddNewTag(e, fileName)}>
                      <input type="text" className="review-popup-new-tag" name="reviewPopupNewTag" placeholder="Add a tag and press enter" />
                    </form>
                    {self.renderTagsTable(imageToTag[fileName], fileName)}
                  </div>
                </div>

              </div>
            )}
          </Popup>
        </div>
      );
    }));

    return imgs;
  }

  /**
   * Renders the list of tags within the image detail popup.
   * Each tag is the trigger for a popup that will allow you to delete the tag.
   */
  renderTagsTable = (tags, fileName) => {
    var self = this;
    var tagElem = [];

    // If tags are not undefined
    if (tags) {
      tagElem.push(tags.map(function (tag, index) {
        return (
          <div className="tag-block" key={tag + index}>
            <span title={tag} className="tag-title">{tag}</span>
            <Popup className="delete-tag-popup" contentStyle={deletePopupContentStyle} trigger={
              <button title="Delete tag" className="delete-tag-button">X</button>
            } modal>
              {close => (
                <div className="modal">
                  <div className="content">
                    {(tags.length === 1) &&
                      <h4>Deleting this tag will delete the image.</h4>
                    }
                    {(tags.length > 1) &&
                      <h4>Are you sure you want to permanently delete this tag?</h4>
                    }
                  </div>
                  <div className="actions">
                    <button className="popUpButton" onClick={() => { close(); }}>Cancel</button>
                    <button className="popUpButton" onClick={() => { self.deleteTag(tag, fileName); close(); }}>Ok</button>
                  </div>
                </div>
              )}
            </Popup>

          </div>
        );
      }));
    }

    return tagElem;
  }

  /**
   * Delete all images that have been selected
   */
  deleteSelectedImages = () => {
    const isImageSelected = this.state.isImageSelected;

    // Loop through each image and delete those that are selected
    for(var fileName in isImageSelected) {
      if(isImageSelected[fileName]) {
        this.onClickImageDelete(fileName);
        delete isImageSelected[fileName];
      }
    }
  }

  onClickImageDelete = (fileName) => {
    const { imageToTag } = this.state;

    // Get all of the folders (tags) this file is in
    var folders = imageToTag[fileName];

    // Delete image in each folder it's in
    for (var i = 0; i < folders.length; i++) {
      this.deleteTag(folders[i], fileName);
    }
  }

  /**
   * Deletes the tag for an image by deleting the image
   * itself from the folder corresponding to the tag.
   */
  deleteTag = (folderName, fileName) => {
    axios
      .post(path + '/review/delete-image',
        {
          folderName: folderName,
          fileName: fileName
        })
      .then(response => {
        // Refresh images
        this.getImages(false);
        this.getImageTagMap();

        // Refresh tags in case deleting image deleted a tag
        this.getTags(false);
      })
      .catch(rejected => {
        console.log(rejected);
      });
  }

  /**
   * Add a new tag to an existing image.
   * This saves the existing image to the folder 
   * corresponding to the tag name.
   */
  onAddNewTag = (e, fileName) => {
    var { nameToImage, imageToTag } = this.state;

    // Keep form from POSTing
    e.preventDefault();

    // Get the new tag name
    var tagName = e.target.reviewPopupNewTag.value;

    // Make sure the image isn't already saved with that tag
    if (!imageToTag[fileName].includes(tagName, 0)) {

      // Save the image with the new tag name
      axios
        .post(path + '/review/add-tag',
          {
            image: nameToImage[fileName],
            tag: tagName,
            imageName: fileName
          })
        .then(response => {
          // Refresh image to tag
          imageToTag[fileName].push(tagName);
          this.setState({
            imageToTag: imageToTag
          });
          
          // Get all tags again in case a new one was added
          this.getTags(false);

          // Update which images were selected based on the tags added
          this.updateSelectedImages();
        })
        .catch(rejected => {
          console.log(rejected);
        });
    }

    // Reset the form
    e.target.reset();
  }

  /**
   * Update if the image is selected for all images.
   */
  updateSelectedImages = () => {
    var { isImageSelected, isTagSelected, imageToTag } = this.state;

    // Get all the file names
    var fileNames = Object.keys(isImageSelected);

    if(!fileNames.entries()) {
      return;
    }

    /* eslint-disable no-unused-vars */
    // Loop through each image and update its selection status
    for(var [index, fileName] of fileNames.entries()) {
      isImageSelected[fileName] = false;

      // Loop through each tag for that image
      if(imageToTag[fileName]) {
        for(var [index2, tag] of imageToTag[fileName].entries()) {
          // This image is selected if any of the tags are selected
          isImageSelected[fileName] = isImageSelected[fileName] || isTagSelected[tag];
        }
      }
    }
    /* eslint-enable no-unused-vars */

    this.setState({
      isImageSelected: isImageSelected
    });
  }

  /**
   * Logic to select images depending on which tag boxes were selected
   */
  handleSelectTag = (e) => {
    var isTagSelected = this.state.isTagSelected;
    var target = e.target;

    /* eslint-disable no-unused-vars */
    // If Select All
    if(target.value === "Select All") {
      // Loop through each tag and set it accordingly
      for(var [index, tag] of this.state.tags.entries()) {
        isTagSelected[tag] = target.checked || document.getElementById("check-box-"+tag).checked;
      }
    }
    else {
      // Update the tag that is selected
      isTagSelected[target.value] = target.checked || document.getElementById("check-box-select-all").checked;
    }
    /* eslint-enable no-unused-vars */

    // Update the images that are selected
    this.updateSelectedImages();
  }

  render() {
    const { loaded, tags } = this.state;

    return (
      <AppWithSideBar listElements={this.sidebarOptions} >
        <div className="review-container">
          {/* Top Filter Bar */}
          <h1>Images</h1>
          <p>Only non uploaded images show up here.</p>
          <div className="review-filter-container">
            {/* Select Tag */}
            <form className="review-filter-form">
                <label key="Select All">
                  {"Select All"}
                  <input className="review-filter-checkbox" type="checkbox" id="check-box-select-all" key="Select All" value="Select All" onChange={this.handleSelectTag}/>
                </label>
              {tags.map((tag) => (
                <label key={tag}>
                  {tag}
                  <input className="review-filter-checkbox" type="checkbox" id={"check-box-"+tag} key={tag} value={tag} onChange={this.handleSelectTag}/>
                </label>
              ))}
            </form>
            {/* Delete Selected Images */}
            <Popup className="delete-Popup" 
                    contentStyle={deletePopupContentStyle} 
                    trigger={<img className="deleteButton" src={DeleteButton} alt="delete"/>} 
                    modal>
              {close => (
                <div className="modal">
                  <div className="content">
                    {" "}
                    Are you sure you want to permanently delete these images?
                  </div>
                  <div className="actions">
                    <button className="popUpButton" onClick={() => { close(); }}>No</button>
                    <button className='popUpButton' onClick={() => { this.deleteSelectedImages(); close(); }}>Yes</button>
                  </div>
                </div>
              )}
            </Popup>
          </div>

          {/* Image Table */}
          <div className="review-image-container">
            {(loaded) && (
              <div className="thumbnail-grid-container">
                {this.renderImageTable()}
              </div>
            )}
          </div>
        </div>
      </AppWithSideBar>
    );
  }
}

export default ReviewPage;