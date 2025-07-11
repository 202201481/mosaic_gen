from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import numpy as np
import io
import json
from optimized_mosaic_generator import OptimizedMosaicGenerator
from fixed_pdf_generator import FixedPDFGenerator

app = Flask(__name__)
CORS(app)

mosaic_gen = OptimizedMosaicGenerator()
pdf_gen = FixedPDFGenerator()

@app.route('/api/generate-mosaic', methods=['POST'])
def generate_mosaic():
    try:
        # Get image file from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        width = int(request.form.get('width', 16))
        height = int(request.form.get('height', 16))
        
        # Open and process the image
        image = Image.open(image_file.stream)
        
        # Generate the mosaic
        mosaic_data = mosaic_gen.generate_mosaic(image, width, height)
        
        return jsonify(mosaic_data)
    
    except Exception as e:
        print(f"Error generating mosaic: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        mosaic_data = data.get('mosaicData')
        settings = data.get('settings')
        
        # Generate PDF
        pdf_buffer = pdf_gen.generate_pdf(mosaic_data, settings)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name='rubiks-mosaic-guide.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
