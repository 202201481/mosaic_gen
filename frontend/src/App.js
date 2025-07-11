import React, { useState } from 'react';
import ImageUploader from './components/ImageUploader';
import MosaicDisplay from './components/MosaicDisplay';
import MosaicControls from './components/MosaicControls';
import Header from './components/Header';
import './App.css';

function App() {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [mosaicData, setMosaicData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mosaicSettings, setMosaicSettings] = useState({
    width: 16,
    height: 16
  });

  const handleImageUpload = (image) => {
    setUploadedImage(image);
    setMosaicData(null); // Clear previous mosaic
  };

  const handleSettingsChange = (settings) => {
    setMosaicSettings(settings);
  };

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <div className="container">
          {!uploadedImage ? (
            <div className="upload-section">
              <h2>Upload Your Photo</h2>
              <p>Upload an image to create a Rubik's cube mosaic</p>
              <ImageUploader onImageUpload={handleImageUpload} />
            </div>
          ) : (
            <div className="mosaic-section">
              <div className="image-preview">
                <h3>Original Image</h3>
                <img 
                  src={uploadedImage} 
                  alt="Uploaded" 
                  className="preview-image"
                />
                <button 
                  className="change-image-btn"
                  onClick={() => setUploadedImage(null)}
                >
                  Change Image
                </button>
              </div>
              
              <MosaicControls 
                settings={mosaicSettings}
                onSettingsChange={handleSettingsChange}
                uploadedImage={uploadedImage}
                onMosaicGenerated={setMosaicData}
                loading={loading}
                setLoading={setLoading}
              />
              
              {mosaicData && (
                <MosaicDisplay 
                  mosaicData={mosaicData}
                  settings={mosaicSettings}
                />
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
