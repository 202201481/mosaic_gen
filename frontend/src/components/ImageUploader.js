import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './ImageUploader.css';

const ImageUploader = ({ onImageUpload }) => {
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        onImageUpload(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    multiple: false
  });

  return (
    <div 
      {...getRootProps()} 
      className={`dropzone ${isDragActive ? 'dropzone-active' : ''}`}
    >
      <input {...getInputProps()} />
      <div className="dropzone-content">
        <div className="upload-icon">📷</div>
        <h3>
          {isDragActive 
            ? 'Drop your image here...' 
            : 'Drag & drop an image here'
          }
        </h3>
        <p>or click to select a file</p>
        <div className="supported-formats">
          <small>Supports: JPG, PNG, GIF, BMP, WebP</small>
        </div>
      </div>
    </div>
  );
};

export default ImageUploader;
