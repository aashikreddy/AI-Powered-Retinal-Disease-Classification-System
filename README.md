# AI-Powered Retinal Disease Classification System

An end-to-end full-stack AI application for classifying diabetic retinopathy from retinal fundus images embedded within medical PDF reports.

## Overview

Diabetic retinopathy is a progressive eye disease associated with diabetes and can lead to vision loss when not identified and managed appropriately. This project explores the use of deep learning to assist diabetic retinopathy screening while integrating the model into a practical document-based workflow.

Unlike a standalone image-classification application, this system accepts a **medical PDF as the primary input**. The application extracts embedded images from the document, preprocesses the retinal image, performs inference using a **DenseNet121 convolutional neural network**, and generates a separate AI-assisted diagnostic report containing the predicted disease stage and model confidence.

The application is implemented as a multi-service architecture:

```text
React Frontend
      │
      ▼
Node.js / Express API
      │
      ▼
Python / FastAPI Inference Service
      │
      ├── PDF Image Extraction
      ├── Image Preprocessing
      ├── DenseNet121 Inference
      └── Diagnostic PDF Generation
      │
      ▼
MongoDB + File Storage
```

> **Disclaimer:** This project is an academic/research prototype. It is not a certified medical device and must not be used as a substitute for professional ophthalmological examination, diagnosis, or treatment.

---

## Problem

Medical imaging workflows often involve retinal images being embedded inside reports or other clinical documents rather than being provided as independent image files.

A conventional image-classification system generally expects:

```text
Image → Model → Prediction
```

This project addresses a broader workflow:

```text
Medical PDF
    ↓
Retinal Image Extraction
    ↓
Image Preprocessing
    ↓
Deep Learning Classification
    ↓
Prediction + Confidence
    ↓
AI-Assisted Diagnostic Report
```

The goal is to demonstrate how a deep-learning model can be integrated into a full-stack application around a document-oriented medical workflow.

---

## Solution

The system combines document processing, computer vision, deep learning, backend APIs, authentication, database persistence, and report generation.

The main workflow is:

1. A user authenticates through the web application.
2. The user uploads a medical PDF.
3. The Node.js backend receives and temporarily stores the PDF.
4. The PDF is forwarded to the Python inference service.
5. PyMuPDF extracts embedded images from the PDF.
6. The extracted image is converted to RGB and resized to `224 × 224`.
7. The image is normalized and passed to the DenseNet121 model.
8. The model produces probabilities for five diabetic retinopathy stages.
9. The highest-probability class is selected.
10. A generated PDF report is created with the prediction and confidence.
11. Report metadata is stored in MongoDB.
12. The generated report can be viewed through report history and downloaded from the dashboard.

---

## Key Features

| Feature | Description |
|---|---|
| Medical PDF ingestion | Accepts PDF reports containing embedded images. |
| PDF image extraction | Extracts embedded images using PyMuPDF. |
| Deep learning classification | Uses DenseNet121 for five-class diabetic retinopathy classification. |
| Five DR stages | No DR, Mild, Moderate, Severe, and Proliferative DR. |
| Image preprocessing | RGB conversion, resizing, normalization, and batching. |
| Confidence estimation | Uses the highest softmax probability as the model confidence. |
| AI-assisted reporting | Generates a separate diagnostic PDF using ReportLab. |
| User authentication | JWT-based authentication with bcrypt password hashing. |
| Report history | Displays previously generated reports through the dashboard. |
| Report download | Allows generated diagnostic reports to be downloaded. |
| REST API architecture | Separates frontend, backend orchestration, and AI inference responsibilities. |
| MongoDB persistence | Stores user accounts and report metadata. |
| Temporary file handling | Uploaded/inference files are processed through temporary storage and cleaned up after processing. |

---

## Diabetic Retinopathy Classification

The deployed model predicts one of five classes:

| Class | Classification |
|---:|---|
| `0` | No Diabetic Retinopathy |
| `1` | Mild Diabetic Retinopathy |
| `2` | Moderate Diabetic Retinopathy |
| `3` | Severe Diabetic Retinopathy |
| `4` | Proliferative Diabetic Retinopathy |

The classifier uses a five-unit softmax output layer:

```text
DenseNet121
      ↓
Global Average Pooling
      ↓
Dropout (0.5)
      ↓
Dense (5)
      ↓
Softmax
```

---

## Machine Learning Model

### DenseNet121

The deployed model is based on **DenseNet121**, a convolutional neural network architecture that uses dense connectivity between layers.

Conceptually:

```text
Input Image
   │
   ▼
DenseNet121 Backbone
   │
   ├── Convolutional Features
   ├── Dense Blocks
   └── Transition Blocks
   │
   ▼
7 × 7 × 1024 Feature Map
   │
   ▼
Global Average Pooling
   │
   ▼
1024 Feature Vector
   │
   ▼
Dropout (0.5)
   │
   ▼
Dense (5)
   │
   ▼
Softmax Probabilities
```

### Model Specifications

| Property | Value |
|---|---|
| Architecture | DenseNet121 |
| Input size | `224 × 224 × 3` |
| Feature map | `7 × 7 × 1024` |
| Pooling | GlobalAveragePooling2D |
| Dropout | `0.5` |
| Output classes | `5` |
| Activation | Softmax |
| Total parameters | `7,042,629` |
| Trainable parameters | `6,958,981` |
| Non-trainable parameters | `83,648` |
| Model artifact | `best_model_latest.h5` |

---

## Inference Pipeline

The deployed inference pipeline transforms an extracted image as follows:

```text
Extracted PDF Image
        │
        ▼
RGB Conversion
        │
        ▼
Resize to 224 × 224
        │
        ▼
float32 Conversion
        │
        ▼
Scale by 1 / 255
        │
        ▼
ImageNet Mean / Standard Deviation Normalization
        │
        ▼
Batch Dimension
        │
        ▼
(1, 224, 224, 3)
        │
        ▼
DenseNet121
        │
        ▼
(1, 5)
        │
        ▼
Argmax
        │
        ▼
Predicted DR Class
```

The model confidence currently corresponds to the maximum value in the softmax output:

```text
confidence = max(probabilities) × 100
```

For example:

```text
[0.001248, 0.028253, 0.059416, 0.290766, 0.620317]
```

produces:

```text
Predicted class: 4
Prediction: Proliferative Diabetic Retinopathy
Confidence: 62.03%
```

A softmax confidence represents the model's output probability distribution and should not be interpreted as clinical certainty.

---

## Dataset

The project documentation references the **APTOS 2019 Blindness Detection Dataset** for diabetic retinopathy classification.

The documented dataset contains five severity categories and has a significant class imbalance.

The project documentation reports:

- **3,662 images**
- **2,929 training images**
- **733 validation images**

The documented class distribution is:

| Class | Images |
|---|---:|
| No DR | 1,434 |
| Mild | 300 |
| Moderate | 808 |
| Severe | 154 |
| Proliferative | 234 |

The current repository does not contain the complete dataset or the original training run associated with the deployed model. Consequently, the exact training/evaluation provenance of the deployed checkpoint cannot be independently reproduced from the repository alone.

---

## Reported Model Performance

The project documentation reports the following evaluation results:

| Metric | Reported Result |
|---|---:|
| Best validation accuracy | **81.82%** |
| Final evaluation accuracy | **81.45%** |
| Weighted precision | **80.48%** |
| Weighted recall | **81.45%** |
| Weighted F1-score | **79.25%** |

Reported AUC values:

| Class | AUC |
|---|---:|
| No DR | 0.9951 |
| Mild DR | 0.8833 |
| Moderate DR | 0.9431 |
| Severe DR | 0.9027 |
| Proliferative DR | 0.9268 |

### Reproducibility

These metrics are **project-reported results**. The repository currently does not contain the complete evaluation dataset, ground-truth labels, prediction outputs, training history, or the exact training script associated with `best_model_latest.h5`.

Therefore, the reported metrics should not be presented as independently reproducible from the current repository.

---

## System Architecture

```text
                         ┌─────────────────────────┐
                         │      React Frontend      │
                         │       Vite + Tailwind    │
                         │        Port 5173         │
                         └────────────┬────────────┘
                                      │
                                      │ REST / Axios
                                      ▼
                         ┌─────────────────────────┐
                         │     Express Backend      │
                         │        Port 5002         │
                         │                         │
                         │ Authentication           │
                         │ JWT Middleware           │
                         │ PDF Upload               │
                         │ Report APIs              │
                         └───────┬─────────┬───────┘
                                 │         │
                                 │         │
                                 ▼         ▼
                    ┌────────────────┐  ┌────────────────┐
                    │ Python FastAPI │  │    MongoDB     │
                    │   Port 8000   │  │   Port 27017   │
                    │                │  │                │
                    │ PDF Processing │  │ Users          │
                    │ Image Pipeline │  │ Reports        │
                    │ ML Inference   │  └────────────────┘
                    │ PDF Generation │
                    └───────┬────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
         ┌─────────┐  ┌────────────┐  ┌────────────┐
         │ PyMuPDF │  │ DenseNet121│  │ ReportLab  │
         │         │  │            │  │            │
         │   PDF   │  │ DR Model   │  │ PDF Report │
         │ Images  │  │            │  │ Generation │
         └─────────┘  └────────────┘  └────────────┘
```

---

## Application Flow

### Authentication

```text
Register
   │
   ▼
Express API
   │
   ▼
bcrypt password hashing
   │
   ▼
MongoDB User
```

Login:

```text
Login
   │
   ▼
Express API
   │
   ├── Find user
   ├── bcrypt password verification
   └── JWT generation
           │
           ▼
        Frontend
           │
           ▼
    Authenticated API requests
```

### PDF Inference

```text
Browser
  │
  │ POST /api/reports/upload
  ▼
Express
  │
  │ Temporary PDF
  ▼
FastAPI
  │
  │ PyMuPDF
  ▼
Embedded Images
  │
  ▼
Preprocessing
  │
  ▼
DenseNet121
  │
  ▼
Prediction + Confidence
  │
  ▼
ReportLab
  │
  ▼
Generated Diagnostic PDF
  │
  ├──────────────► Filesystem
  │
  └──────────────► MongoDB metadata
```

### Report Retrieval

```text
Dashboard
   │
   ├── GET /api/reports/history
   │
   └── GET /api/reports/download/:id
                         │
                         ▼
                    Express API
                         │
                         ▼
                    Report Metadata
                         │
                         ▼
                    Generated PDF
```

---

## Project Structure

```text
.
├── src/
│   ├── components/
│   │   ├── Navbar.*
│   │   ├── UploadSection.jsx
│   │   └── ReportHistory.jsx
│   │
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── Dashboard.*
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── App.tsx
│   └── main.tsx
│
├── backend/
│   ├── middleware/
│   │   └── auth.js
│   │
│   ├── models/
│   │   ├── User.js
│   │   └── Report.js
│   │
│   ├── routes/
│   │   ├── auth.js
│   │   └── reports.js
│   │
│   ├── uploads/
│   ├── temp_inference/
│   ├── ai_diagnostic_reports/
│   ├── inference.py
│   └── server.js
│
├── best_model_latest.h5
├── ResNet50_best.h5
├── finaloutputpdfgenerator.py
├── Untitled1 (1).ipynb
├── package.json
└── README.md
```

---

## Technology Stack

### Frontend

- React 18
- TypeScript / JSX
- Vite
- Tailwind CSS
- Axios
- Lucide React

### Backend

- Node.js
- Express.js
- MongoDB
- Mongoose
- JWT
- bcryptjs
- Multer
- FormData

### AI / Computer Vision

- Python 3.11
- FastAPI
- Uvicorn
- TensorFlow
- Keras / `tf_keras`
- DenseNet121
- NumPy
- Pillow
- OpenCV
- PyMuPDF

### Report Generation

- ReportLab

---

## API

### Authentication

#### Register

```http
POST /api/auth/register
```

Creates a new user account.

#### Login

```http
POST /api/auth/login
```

Authenticates a user and returns a JWT.

---

### Reports

#### Upload Report

```http
POST /api/reports/upload
```

Authenticated endpoint.

Multipart form field:

```text
pdf
```

#### Report History

```http
GET /api/reports/history
```

Returns report records associated with the authenticated account in the intended ownership model.

#### Download Report

```http
GET /api/reports/download/:id
```

Downloads a generated diagnostic PDF.

---

### Inference Service

#### Health

```http
GET /health
```

Returns the health status of the inference service and model-loading state.

#### PDF Inference

```http
POST /infer_pdf
```

Accepts a PDF and performs the image extraction, preprocessing, model inference, and report-generation workflow.

---

## Installation

### Prerequisites

- Node.js
- npm
- Python 3.11
- MongoDB
- Git

Verify the installed versions:

```bash
node --version
npm --version
python --version
git --version
```

### Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### Install Node Dependencies

```bash
npm install
```

Install backend dependencies according to the backend package configuration.

### Python Environment

Create and activate a Python virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

The deployed legacy HDF5 model requires the Keras compatibility environment used by the inference service.

---

## Environment Configuration

Configure the backend environment with values appropriate for the local installation.

Example:

```env
MONGODB_URI=mongodb://localhost:27017/retinal_disease
JWT_SECRET=your_secure_secret
PORT=5002
FASTAPI_URL=http://localhost:8000
```

For production deployments, secrets must be supplied through a secure secret-management mechanism rather than committed to source control.

---

## Running Locally

The application consists of three services.

### 1. Start the AI Inference Service

```powershell
cd backend
.\.venv\Scripts\activate
$env:PYTHONIOENCODING="utf-8"
python inference.py
```

FastAPI:

```text
http://localhost:8000
```

### 2. Start the Express Backend

```powershell
cd backend
npm start
```

Backend:

```text
http://localhost:5002
```

### 3. Start the React Frontend

From the project root:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Example Prediction

For a retinal image processed by the deployed model, the model may produce a probability vector such as:

```text
No DR          0.12%
Mild DR        2.83%
Moderate DR    5.94%
Severe DR     29.08%
Proliferative 62.03%
```

The resulting classification is:

```text
Proliferative Diabetic Retinopathy
Confidence: 62.03%
```

The prediction is then used by the report-generation pipeline to produce an AI-assisted diagnostic PDF.

---

## Security

The application includes JWT-based authentication and bcrypt password hashing.

The architecture separates:

- authentication
- API orchestration
- AI inference
- persistence
- generated-file storage

Security hardening remains an area of ongoing development, particularly around report ownership and authorization, input validation, internal inference-service access, and production deployment controls.

The system should not be exposed directly to clinical or public traffic without appropriate security review, authorization controls, infrastructure hardening, monitoring, and validation.

---

## Limitations

### PDF Image Selection

The current implementation extracts images from a PDF but uses the first extracted image for model inference.

If a document contains multiple images, the first image may not necessarily be the retinal fundus image.

### Non-Retinal Images

The deployed classifier contains five diabetic retinopathy classes and does not have a dedicated `Not a Retina` class.

A non-retinal image can therefore still produce a softmax probability distribution across the five DR categories.

### Model Provenance

The deployed model artifact is available, but the complete training and evaluation pipeline associated with that artifact is not currently available in the repository.

The exact:

- training script
- dataset copy/version
- training history
- evaluation predictions
- evaluation labels
- original training configuration

cannot currently be independently reconstructed from the available repository artifacts.

### Clinical Validation

The project has not been established as a clinically validated diagnostic system.

Performance on the documented dataset should not be interpreted as evidence of clinical effectiveness in real-world patient populations.

### Data Imbalance

The referenced dataset contains substantially different numbers of samples across severity classes, particularly for Mild and Severe categories.

Class imbalance can affect model learning and evaluation.

---

## Future Improvements

Potential improvements include:

- Robust retinal-image selection for multi-image PDFs
- Dedicated retinal vs non-retinal image validation
- Out-of-distribution detection
- Model calibration
- Explainable AI using Grad-CAM or similar techniques
- Preservation of the complete model probability vector
- Model versioning and inference metadata
- Reproducible training and evaluation pipelines
- Stronger API authorization and report ownership
- Secure internal communication between backend services
- Upload size and resource controls
- Automated unit and integration testing
- Structured application logging
- Containerized deployment
- CI/CD integration
- Role-based access control
- External validation using independent datasets

---

## Development Status

| Component | Status |
|---|---|
| React web application | Functional |
| User registration | Functional |
| JWT authentication | Functional |
| Express REST API | Functional |
| MongoDB integration | Functional |
| PDF upload | Functional |
| PDF image extraction | Functional |
| DenseNet121 inference | Functional |
| Five-class DR classification | Functional |
| AI-generated PDF report | Functional |
| Report history | Functional, authorization hardening required |
| Report download | Functional, authorization hardening required |
| Multi-image PDF handling | Improvement required |
| Training reproducibility | Incomplete |
| Automated test suite | Planned |
| Clinical deployment | Not suitable in current state |

---

## Academic Scope

This project demonstrates the integration of several areas of software engineering and artificial intelligence:

- Deep learning
- Medical image classification
- Convolutional neural networks
- Transfer learning
- Computer vision preprocessing
- PDF document processing
- RESTful API design
- Full-stack web development
- JWT authentication
- MongoDB data persistence
- AI inference services
- Automated PDF report generation

The project focuses on connecting a deep-learning image classifier with a practical document-processing workflow rather than treating image classification as an isolated model-only problem.

---

## Disclaimer

This software is provided for **academic and research purposes only**.

It is not a certified medical device and has not been validated for clinical diagnosis or treatment decisions.

Predictions generated by the model may be incorrect. Model confidence is not equivalent to medical certainty. Any real-world medical interpretation must be performed by an appropriately qualified healthcare professional.

---

## Author

**Aashik Reddy Thatiparthi**

Computer Science & Engineering

