# Hospital AI Backend

Node.js/Express backend for the Hospital AI web application.

## Quick Start

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env and set your configuration
nano .env

# Start the server
npm start
```

## Environment Variables

Create a `.env` file with:

```env
MONGODB_URI=mongodb://localhost:27017/hospital-ai
JWT_SECRET=your-very-secure-secret-key-change-this
PORT=5000
FASTAPI_URL=http://localhost:5001
```

## API Documentation

### Authentication Endpoints

#### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "doctor@hospital.com",
  "password": "securepassword"
}

Response:
{
  "message": "User registered successfully",
  "token": "jwt-token-here",
  "user": {
    "id": "user-id",
    "email": "doctor@hospital.com"
  }
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "doctor@hospital.com",
  "password": "securepassword"
}

Response:
{
  "message": "Login successful",
  "token": "jwt-token-here",
  "user": {
    "id": "user-id",
    "email": "doctor@hospital.com"
  }
}
```

### Report Endpoints

All report endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

#### Upload Report
```
POST /api/reports/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- pdf: <PDF file>

Response:
{
  "message": "Report processed successfully",
  "report": {
    "id": "report-id",
    "original_filename": "medical_report.pdf",
    "prediction": "Moderate DR",
    "confidence": 0.91,
    "output_pdf": "reports/AI_Report_123.pdf",
    "createdAt": "2024-01-15T10:30:00.000Z"
  }
}
```

#### Get Report History
```
GET /api/reports/history
Authorization: Bearer <token>

Response:
{
  "reports": [
    {
      "_id": "report-id",
      "original_filename": "medical_report.pdf",
      "prediction": "Moderate DR",
      "confidence": 0.91,
      "output_pdf": "reports/AI_Report_123.pdf",
      "createdAt": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

#### Download Report
```
GET /api/reports/download/:id
Authorization: Bearer <token>

Response: PDF file download
```

## FastAPI Integration

The backend forwards PDF uploads to the FastAPI service at `http://localhost:5001/process-report`

Expected FastAPI Response:
```json
{
  "prediction": "Moderate DR",
  "confidence": 0.91,
  "output_pdf": "reports/AI_Report_123.pdf"
}
```

## Development

```bash
# Run with auto-reload (Node 18+)
npm run dev
```

## Production

1. Set strong `JWT_SECRET`
2. Use production MongoDB (e.g., MongoDB Atlas)
3. Configure CORS for your domain
4. Use PM2 or similar for process management
5. Enable HTTPS
6. Set up logging and monitoring
