import React from 'react';
import axios from 'axios';
import './MosaicControls.css';

const MosaicControls = ({ 
  settings, 
  onSettingsChange, 
  uploadedImage, 
  onMosaicGenerated, 
  loading, 
  setLoading 
}) => {
  const handleWidthChange = (e) => {
    onSettingsChange({
      ...settings,
      width: parseInt(e.target.value)
    });
  };

  const handleHeightChange = (e) => {
    onSettingsChange({
      ...settings,
      height: parseInt(e.target.value)
    });
  };

  const generateMosaic = async () => {
    if (!uploadedImage) return;
    
    setLoading(true);
    try {
      // Convert data URL to blob
      const response = await fetch(uploadedImage);
      const blob = await response.blob();
      
      // Create FormData
      const formData = new FormData();
      formData.append('image', blob, 'image.jpg');
      formData.append('width', settings.width);
      formData.append('height', settings.height);
      
      // Send to backend
      const result = await axios.post('/api/generate-mosaic', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      onMosaicGenerated(result.data);
    } catch (error) {
      console.error('Error generating mosaic:', error);
      alert('Error generating mosaic. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mosaic-controls">
      <h3>Mosaic Settings</h3>
      
      <div className="control-group">
        <label htmlFor="width">Width (cubes):</label>
        <input
          id="width"
          type="range"
          min="8"
          max="32"
          value={settings.width}
          onChange={handleWidthChange}
          className="slider"
        />
        <span className="value">{settings.width}</span>
      </div>
      
      <div className="control-group">
        <label htmlFor="height">Height (cubes):</label>
        <input
          id="height"
          type="range"
          min="8"
          max="32"
          value={settings.height}
          onChange={handleHeightChange}
          className="slider"
        />
        <span className="value">{settings.height}</span>
      </div>
      
      <div className="total-cubes">
        <strong>Total cubes needed: {settings.width * settings.height}</strong>
      </div>
      
      <button 
        className="generate-btn"
        onClick={generateMosaic}
        disabled={loading || !uploadedImage}
      >
        {loading ? (
          <>
            <span className="spinner"></span>
            Generating...
          </>
        ) : (
          'Generate Mosaic'
        )}
      </button>
    </div>
  );
};

export default MosaicControls;
