"""
FastAPI Inference Server for Diabetic Retinopathy Detection
Workflow: PDF Input -> Image Extraction -> ResNet50 Model Inference -> PDF Output
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import FileResponse
import uvicorn
import os
import sys
import tempfile
import numpy as np
from datetime import datetime
import shutil
import secrets

# Enable legacy tf.keras loader to accept older layer names (e.g., containing '/').
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

# ML & Image Processing
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import cv2

# PDF Processing
import PyPDF2
import fitz  # PyMuPDF for better PDF handling

from finaloutputpdfgenerator import generate_ai_report

# =========================================
# CONFIGURATION
# =========================================

# Use absolute paths for reliability
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'best_model_latest.h5')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'ai_diagnostic_reports')
UPLOAD_DIR = os.path.join(SCRIPT_DIR, 'uploads')
TEMP_DIR = os.path.join(SCRIPT_DIR, 'temp_inference')

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Image preprocessing constants
IMG_SIZE = 224
MEAN = np.array([0.485, 0.456, 0.406])
STD = np.array([0.229, 0.224, 0.225])

# =========================================
# INITIALIZE FASTAPI APP
# =========================================

app = FastAPI(title="Diabetic Retinopathy Inference API")

# =========================================
# LOAD MODEL
# =========================================

try:
    if not os.path.exists(MODEL_PATH):
        print(f"✗ Model file not found at: {MODEL_PATH}")
        model = None
    else:
        print(f"✓ Loading model from: {MODEL_PATH}")
        try:
            # Primary attempt: modern loader with legacy allowed
            model = load_model(MODEL_PATH, compile=False, safe_mode=False)
            print(f"✓ Model loaded successfully")
        except Exception as e:
            print(f"⚠ Primary load_model failed ({e}); retrying with tf.compat.v1 loader...")
            try:
                model = tf.compat.v1.keras.models.load_model(MODEL_PATH, compile=False)
                print(f"✓ Model loaded via tf.compat.v1.keras")
            except Exception as e2:
                print(f"⚠ tf.compat.v1 loader failed ({e2}); retrying with tf_keras legacy loader if available...")
                try:
                    import tf_keras

                    model = tf_keras.models.load_model(MODEL_PATH, compile=False)
                    print("✓ Model loaded via tf_keras legacy loader")
                except Exception as e3:
                    print(f"✗ Error loading model: {e3}")
                    model = None
except Exception as e:
    print(f"✗ Error loading model: {e}")
    model = None

# =========================================
# HELPER FUNCTIONS
# =========================================

def extract_images_from_pdf(pdf_path):
    """
    Extract images from PDF using PyMuPDF for better quality.
    Returns list of image file paths.
    """
    images = []
    try:
        # Try PyMuPDF first (better quality)
        pdf_document = fitz.open(pdf_path)
        
        total_images = sum(len(page.get_images()) for page in pdf_document)
        if total_images > 50:
            pdf_document.close()
            raise HTTPException(status_code=400, detail="PDF contains too many images, maximum allowed is 50")
            

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()
            
            if image_list:
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_document, xref)
                    
                    image_filename = os.path.join(
                        TEMP_DIR, 
                        f"extracted_page{page_num}_img{img_index}.png"
                    )
                    
                    if pix.n - pix.alpha < 4:  # Grayscale or RGB
                        pix.save(image_filename)
                    else:  # RGBA
                        pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                        pix_rgb.save(image_filename)
                    
                    images.append({
                        "path": image_filename,
                        "width": pix.w,
                        "height": pix.h,
                        "area": pix.w * pix.h
                    })
        
        pdf_document.close()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Warning: PyMuPDF extraction failed: {e}, trying PyPDF2...")
        
        # Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                if len(pdf_reader.pages) > 0:
                    # Try to extract from first page
                    print(f"✓ PDF has {len(pdf_reader.pages)} pages")
        except Exception as e2:
            print(f"✗ PyPDF2 also failed: {e2}")
    
    return images

def preprocess_image(image_path):
    """
    Preprocess image for ResNet50 model.
    Returns numpy array ready for model inference.
    """
    try:
        # Load image
        img = Image.open(image_path).convert('RGB')
        
        # Resize to model input size
        img = img.resize((IMG_SIZE, IMG_SIZE))
        
        # Convert to numpy array
        img_array = np.array(img, dtype=np.float32)
        
        # Normalize to [0, 1]
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    except Exception as e:
        print(f"✗ Error preprocessing image: {e}")
        return None

def run_inference(image_array):
    """
    Run model inference on preprocessed image.
    Returns predicted class and confidence score.
    """
    if model is None:
        raise Exception("Model not loaded")
    
    try:
        predictions = model.predict(image_array, verbose=0)
        predicted_class = int(np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0])) * 100
        
        return predicted_class, confidence
    
    except Exception as e:
        print(f"✗ Error during inference: {e}")
        raise

def generate_output_pdf(
    image_path,
    predicted_class,
    confidence,
    patient_info=None
):
    """
    Generate final diagnostic PDF using finaloutputpdfgenerator.
    """
    if patient_info is None:
        patient_info = {
            "name": "Patient",
            "id": "ID_001",
            "age": "N/A",
            "gender": "N/A",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "doctor": "AI Diagnostic System"
        }
    
    # Generate unique output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"AI_Report_{timestamp}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        generate_ai_report(
            output_pdf=output_path,
            patient_info=patient_info,
            image_path=image_path,
            predicted_class=predicted_class,
            confidence=confidence
        )
        return output_path
    
    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        raise

# =========================================
# API ENDPOINTS
# =========================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/infer_pdf")
async def infer_pdf(file: UploadFile = File(...), x_internal_secret: str = Header(None)):
    """
    Main inference endpoint.
    Accepts PDF, extracts images, runs inference, returns output PDF.
    """
    expected_secret = os.getenv("INTERNAL_API_KEY")
    if not expected_secret:
        env_path = os.path.join(SCRIPT_DIR, '.env')
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('INTERNAL_API_KEY='):
                        expected_secret = line.strip().split('=', 1)[1]
                        break
        except Exception:
            pass

    if not expected_secret or not x_internal_secret or not secrets.compare_digest(expected_secret, x_internal_secret):
        raise HTTPException(status_code=401, detail="Unauthorized")
    pdf_path = None
    extracted_images = []
    
    try:
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        import uuid
        
        # Save uploaded PDF temporarily with a safe filename
        safe_filename = f"{uuid.uuid4()}.pdf"
        pdf_path = os.path.join(TEMP_DIR, safe_filename)
        with open(pdf_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        print(f"✓ PDF received: {file.filename}")
        print(f"✓ PDF saved to: {pdf_path}")
        
        # Extract images from PDF
        extracted_images = extract_images_from_pdf(pdf_path)
        
        if not extracted_images:
            print(f"✗ No images found in PDF: {pdf_path}")
            raise HTTPException(
                status_code=400,
                detail="No images found in PDF. Please ensure the PDF contains at least one image."
            )
        
        print(f"✓ Extracted {len(extracted_images)} image(s) from PDF")
        
        # Select the image with the largest pixel area
        selected_image = max(extracted_images, key=lambda x: x["area"])
        image_path = selected_image["path"]
        print(f"✓ Selected largest image: {selected_image['width']}x{selected_image['height']} (Area: {selected_image['area']})")
        
        # Preprocess image
        img_array = preprocess_image(image_path)
        if img_array is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to preprocess image"
            )
        
        print(f"✓ Image preprocessed: {image_path}")
        
        # Run inference
        predicted_class, confidence = run_inference(img_array)
        
        print(f"✓ Inference complete: Class={predicted_class}, Confidence={confidence:.2f}%")
        
        # Generate output PDF
        output_pdf_path = generate_output_pdf(
            image_path=image_path,
            predicted_class=predicted_class,
            confidence=confidence
        )
        
        # Return just the filename - Express will find it in ai_diagnostic_reports/
        output_filename = os.path.basename(output_pdf_path)
        
        response_data = {
            "prediction": predicted_class,
            "confidence": confidence,
            "output_pdf": output_filename,
            "message": "Inference completed successfully"
        }
        
        print(f"✓ Response prepared: {response_data}")
        
        return response_data
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        print(f"✗ Error in inference: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temporary files
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except:
                pass
        
        for img_item in extracted_images:
            img_path = img_item["path"] if isinstance(img_item, dict) else img_item
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except:
                    pass

@app.get("/class_info/{class_id}")
async def get_class_info(class_id: int):
    """Get information about a predicted class"""
    class_map = {
        0: "No Diabetic Retinopathy",
        1: "Mild Diabetic Retinopathy",
        2: "Moderate Diabetic Retinopathy",
        3: "Severe Diabetic Retinopathy",
        4: "Proliferative Diabetic Retinopathy"
    }
    
    if class_id not in class_map:
        raise HTTPException(status_code=404, detail="Class not found")
    
    return {
        "class_id": class_id,
        "name": class_map[class_id]
    }

# =========================================
# MAIN
# =========================================

if __name__ == "__main__":
    if model is None:
        print("⚠ Warning: Model could not be loaded. The API will still run but inference will fail.")
    
    print("\n" + "="*50)
    print("Starting Inference Server...")
    print("="*50)
    print(f"Model path: {MODEL_PATH}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*50 + "\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
