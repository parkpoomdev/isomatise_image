# Isometric Image Transformer

A web application that transforms images into isometric projections with various orientations and width variants.

## Features

- Upload images in various formats (PNG, JPG, JPEG, GIF, BMP, TIFF)
- Generate 24 different isometric variants:
  - 4 width variants: very_narrow, narrow, medium, wide
  - 6 orientations per width: up, down, left, right, left+CCW30°, right+CCW30°
- **Automatic local file saving**: All processed images are automatically saved to the `outputs/` folder
- Download processed images individually from the web interface
- View saved files information and folder location
- Modern, responsive web interface

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and go to: http://localhost:5000

## Usage

1. Click "Choose Image File" to select an image
2. Preview your selected image
3. Click "Process Image" to generate isometric variants
4. **All 24 processed images are automatically saved to the `outputs/` folder**
5. Download individual processed images using the download buttons
6. Click "View Saved Files" to see information about locally saved files

## Technical Details

The application uses:
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Backend**: Flask (Python web framework)
- **Image Processing**: PIL/Pillow for image transformations
- **Mathematical Transformations**: 
  - Isometric scaling (30° angle)
  - Shear transformations for perspective effects
  - Rotation for additional orientations

## File Structure

- `index.html` - Main web interface
- `app.py` - Flask backend server
- `requirements.txt` - Python dependencies
- `image_transformer.py` - Original standalone image processing script
