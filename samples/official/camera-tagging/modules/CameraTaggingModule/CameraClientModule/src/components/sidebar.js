import React from 'react';
import PropTypes from 'prop-types';
import LogoBar from './logo-bar'
import '../styles/sidebar.css'

const SidebarProps = {
  listElements: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      handleClick: PropTypes.func,
      children: PropTypes.array
    })
  )
};

/**
 * The side navigation bar of the web page.
 * It takes as input an array of JSON objects
 * with the name of the page, whether that is the active page,
 * and what to do when the name is clicked on.
 */
export const Sidebar = ({ listElements = [] }) => {
  return (
      <div className="sidebar">
        <div className="sidebar-list">
          {listElements.map(
            ({ name, handleClick, children = [], isActive = false }, index) => (
              <div
                className={ isActive ? `listItem active` : 'listItem' }
                key={name}
                onClick={
                  typeof handleClick === 'function'
                    ? () => handleClick(name)
                    : null
                }
              >
                <p>{name}</p>
                {children.length > 0 && children.map(child => <p>{child}</p>)}
              </div>
            )
          )}
        </div>
      </div>
  );
};

Sidebar.propTypes = SidebarProps;

/**
 * This component is a template with the side
 * navigation bar and logo bar already in place.
 * It places the rest of the elements of a page appropriately.
 */
export const AppWithSideBar = ({ children, ...props }) => {
  return (
    <div className='container'>
      <LogoBar />
      <div className='page-container'>
        <Sidebar {...props} />
        <div className='right-child'>{children}</div>
      </div>
    </div>
  );
};

AppWithSideBar.propTypes = SidebarProps;

export default AppWithSideBar;