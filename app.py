from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
import io
from PIL import Image
import math
import uuid

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def base64_to_image(base64_str):
    """Convert base64 string back to PIL Image"""
    img_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_data))

def save_processed_images(results):
    """Save processed images to local output folder"""
    import time
    timestamp = int(time.time())

    # Create a timestamped subdirectory inside OUTPUT_FOLDER
    timestamp_dir = os.path.join(OUTPUT_FOLDER, str(timestamp))
    os.makedirs(timestamp_dir, exist_ok=True)

    for result in results:
        # Use the original result name, saved inside the timestamp directory
        filename = result['name']
        filepath = os.path.join(timestamp_dir, filename)

        # Convert base64 back to image and save
        image = base64_to_image(result['image'])
        image.save(filepath)
        # Print the relative saved path for easier reading in logs
        print(f"Saved: {os.path.join(str(timestamp), filename)}")

def autocrop_rgba(img, pad=0):
    """Auto-crop image based on alpha channel"""
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(img.width,  x1 + pad); y1 = min(img.height, y1 + pad)
    return img.crop((x0, y0, x1, y1))

def shear_y_up(img, k, pad=8):
    """Shear image upward"""
    new_w = img.width
    new_h = int(round(img.height + k * img.width))
    a, b, c = 1, 0, 0
    d, e, f = -k, 1, 0
    out = img.transform((new_w, new_h), Image.AFFINE, (a, b, c, d, e, f), Image.BICUBIC)
    return autocrop_rgba(out, pad)

def shear_y_down(img, k, pad=8):
    """Shear image downward"""
    new_w = img.width
    offset = int(round(k * img.width))
    new_h = img.height + offset
    a, b, c = 1, 0, 0
    d, e, f = k, 1, -offset
    out = img.transform((new_w, new_h), Image.AFFINE, (a, b, c, d, e, f), Image.BICUBIC)
    return autocrop_rgba(out, pad)

def shear_x_right(img, k, pad=8):
    """Shear image to the right"""
    new_w = int(round(img.width + k * img.height))
    new_h = img.height
    a, b, c = 1, -k, 0
    d, e, f = 0,  1, 0
    out = img.transform((new_w, new_h), Image.AFFINE, (a, b, c, d, e, f), Image.BICUBIC)
    return autocrop_rgba(out, pad)

def shear_x_left(img, k, pad=8):
    """Shear image to the left"""
    offset = int(round(k * img.height))
    new_w = img.width + offset
    new_h = img.height
    a, b, c = 1, k, -offset
    d, e, f = 0, 1, 0
    out = img.transform((new_w, new_h), Image.AFFINE, (a, b, c, d, e, f), Image.BICUBIC)
    return autocrop_rgba(out, pad)

def process_isometric_image(image_path):
    """Process image and return all isometric variants"""
    try:
        # Load and convert image
        im0 = Image.open(image_path).convert("RGBA")
        w0, h0 = im0.size
        
        # Isometric parameters
        scale_y = math.cos(math.radians(30))   # ≈ 0.866
        k = math.tan(math.radians(30))         # ≈ 0.577
        
        # Width variants
        width_variants = {
            "very_narrow": 0.60,
            "narrow":      0.80,
            "medium":      1.00,
            "wide":        1.25
        }
        
        results = []
        
        for label, sx in width_variants.items():
            # 1) Scale width
            w1 = max(1, int(round(w0 * sx)))
            h1 = h0
            im_xscaled = im0.resize((w1, h1), Image.BICUBIC)
            
            # 2) Scale height for isometric
            h_iso = max(1, int(round(h1 * scale_y)))
            im_iso = im_xscaled.resize((w1, h_iso), Image.BICUBIC)
            
            # 3) Shear up/down
            up_img = shear_y_up(im_iso, k)
            dn_img = shear_y_down(im_iso, k)
            
            # 4) Shear left/right
            left_img = shear_x_left(im_iso, k)
            right_img = shear_x_right(im_iso, k)
            
            # 5) Rotate left/right images
            left_rot = autocrop_rgba(left_img.rotate(30, resample=Image.BICUBIC, expand=True), 8)
            right_rot = autocrop_rgba(right_img.rotate(30, resample=Image.BICUBIC, expand=True), 8)
            
            # Convert to base64 and add to results
            variants = [
                ("isometric_up_" + label, up_img),
                ("isometric_down_" + label, dn_img),
                ("isometric_left_" + label, left_img),
                ("isometric_right_" + label, right_img),
                ("isometric_left_ccw30_" + label, left_rot),
                ("isometric_right_ccw30_" + label, right_rot)
            ]
            
            for name, img in variants:
                results.append({
                    "name": name + ".png",
                    "image": image_to_base64(img)
                })
        
        return results
        
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/process', methods=['POST'])
def process_image():
    """Process uploaded image and return isometric variants"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload an image file.'})
        
        # Generate unique filename
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save uploaded file
        file.save(filepath)
        
        # Process image
        results = process_isometric_image(filepath)
        
        # Save processed images to local folder
        save_processed_images(results)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/saved-files')
def saved_files():
    """List all saved processed images"""
    try:
        files = []
        if os.path.exists(OUTPUT_FOLDER):
            # Walk subdirectories so we find files saved inside timestamp folders
            for dirpath, dirnames, filenames in os.walk(OUTPUT_FOLDER):
                # Determine subfolder relative to OUTPUT_FOLDER (e.g., the timestamp folder)
                rel_dir = os.path.relpath(dirpath, OUTPUT_FOLDER)
                if rel_dir == '.':
                    rel_dir = ''

                for filename in filenames:
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        filepath = os.path.join(dirpath, filename)
                        file_size = os.path.getsize(filepath)
                        file_time = os.path.getmtime(filepath)
                        files.append({
                            'name': filename,
                            'size': file_size,
                            'modified': file_time,
                            'subfolder': rel_dir,  # e.g. '169...' timestamp or '' for root
                            'path': os.path.abspath(filepath)
                        })

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({
            'success': True,
            'files': files,
            'output_folder': os.path.abspath(OUTPUT_FOLDER)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/outputs/<path:filename>')
def serve_output_file(filename):
    """Serve saved output files (supports subfolders)"""
    # send_from_directory will safely serve files under OUTPUT_FOLDER
    try:
        return send_from_directory(OUTPUT_FOLDER, filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

if __name__ == '__main__':
    print("Starting Isometric Image Transformer Server...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
