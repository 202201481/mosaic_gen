import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <h1 className="header-title">
          <div className="cube-icon">
            <div className="rubiks-cube">
              <div className="cube-row">
                <div className="cube-cell red"></div>
                <div className="cube-cell white"></div>
                <div className="cube-cell blue"></div>
              </div>
              <div className="cube-row">
                <div className="cube-cell green"></div>
                <div className="cube-cell yellow"></div>
                <div className="cube-cell orange"></div>
              </div>
              <div className="cube-row">
                <div className="cube-cell blue"></div>
                <div className="cube-cell red"></div>
                <div className="cube-cell white"></div>
              </div>
            </div>
          </div>
          Rubik's Cube Mosaic Generator
        </h1>
        <p className="header-subtitle">
          Transform your photos into colorful Rubik's cube mosaics
        </p>
      </div>
    </header>
  );
};

export default Header;
