import React from 'react';
import axios from 'axios';
import './MosaicDisplay.css';

const MosaicDisplay = ({ mosaicData, settings }) => {
  const downloadPDF = async () => {
    try {
      const response = await axios.post('/api/generate-pdf', {
        mosaicData: mosaicData,
        settings: settings
      }, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'rubiks-mosaic-guide.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Error generating PDF. Please try again.');
    }
  };

  const getRubikColorName = (color) => {
    const colorMap = {
      '#FFFFFF': 'White',
      '#FFD500': 'Yellow',
      '#FF5800': 'Orange',
      '#C41E3A': 'Red',
      '#009E60': 'Green',
      '#0051BA': 'Blue'
    };
    return colorMap[color] || 'Unknown';
  };

  if (!mosaicData) {
    return null;
  }

  return (
    <div className="mosaic-display">
      <h3>Your Rubik's Cube Mosaic</h3>
      
      <div className="mosaic-overview">
        <div className="mosaic-info">
          <p>
            <strong>Cube Grid:</strong> {settings.width}×{settings.height} cubes 
            ({mosaicData.dimensions?.total || settings.width * settings.height} total)
          </p>
          <p>
            <strong>Display Resolution:</strong> {mosaicData.dimensions?.display_width || settings.width * 3}×{mosaicData.dimensions?.display_height || settings.height * 3} pixels 
            (3×3 faces per cube)
          </p>
        </div>
        
        <div className="mosaic-grid" style={{
          gridTemplateColumns: `repeat(${mosaicData.dimensions?.display_width || settings.width * 3}, 1fr)`,
          gridTemplateRows: `repeat(${mosaicData.dimensions?.display_height || settings.height * 3}, 1fr)`
        }}>
          {mosaicData.grid && mosaicData.grid.map((row, rowIndex) =>
            row.map((faceColor, colIndex) => (
              <div
                key={`${rowIndex}-${colIndex}`}
                className="face-cell"
                style={{ backgroundColor: faceColor }}
                title={`Face: ${getRubikColorName(faceColor)}`}
              />
            ))
          )}
        </div>
      </div>
      
      {mosaicData.colorCount && (
        <div className="color-summary">
          <h4>Total Faces Needed by Color:</h4>
          <div className="color-list">
            {Object.entries(mosaicData.colorCount).map(([color, count]) => (
              <div key={color} className="color-item">
                <div 
                  className="color-swatch" 
                  style={{ backgroundColor: color }}
                ></div>
                <span className="color-name">{getRubikColorName(color)}</span>
                <span className="color-count">{count} faces</span>
              </div>
            ))}
          </div>
          <div className="total-info">
            <p><strong>Total Cubes:</strong> {mosaicData.dimensions.total}</p>
            <p><strong>Total Faces:</strong> {mosaicData.dimensions.total_faces}</p>
          </div>
        </div>
      )}
      
      <div className="download-section">
        <button className="download-btn" onClick={downloadPDF}>
          📄 Download Detailed PDF Guide
        </button>
        <p className="download-note">
          The PDF will contain detailed 4×3 cube layouts per page showing exactly how to configure each cube's faces.
        </p>
      </div>
    </div>
  );
};

export default MosaicDisplay;
