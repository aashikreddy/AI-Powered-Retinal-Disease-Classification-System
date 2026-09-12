"""
Setup and Installation Instructions for Inference Server
"""

# Required Python packages for inference:

PACKAGES = [
    "fastapi>=0.104.0",           # API framework
    "uvicorn>=0.24.0",            # ASGI server
    "tensorflow>=2.13.0",         # Deep learning framework
    "opencv-python>=4.8.0",       # Computer vision
    "Pillow>=10.0.0",             # Image processing
    "PyPDF2>=4.0.0",              # PDF reading (fallback)
    "pymupdf>=1.23.0",            # PDF extraction (primary)
    "numpy>=1.24.0",              # Numerical computing
    "reportlab>=4.0.0",           # PDF generation (already used)
]

# Installation command:
# pip install fastapi uvicorn tensorflow opencv-python Pillow PyPDF2 pymupdf numpy reportlab

# =========================================
# Setup Steps
# =========================================

"""
1. Install Dependencies:
   pip install -r requirements_inference.txt
   
2. Ensure Model File Exists:
   - Place ResNet50_best.h5 in the project root directory
   
3. Run the Inference Server:
   python backend/inference.py
   
   The server will start on http://localhost:8000
   
4. API Endpoints:
   - GET /health              : Health check
   - POST /infer_pdf          : Upload PDF and get diagnostic report
   - GET /class_info/{id}     : Get class information
   
5. Test the API:
   curl -X POST "http://localhost:8000/infer_pdf" -F "file=@sample.pdf"
   
6. API Documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   
7. Integration:
   - The backend/routes/reports.js already expects /infer_pdf endpoint
   - Ensure FASTAPI_URL environment variable points to http://localhost:8000
"""
