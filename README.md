# Hospital AI Web Application

A professional medical report analysis platform that integrates with a FastAPI ML service for AI-powered diagnostic predictions.

## Architecture

```
React Frontend → Node.js/Express Backend → FastAPI ML Service
       ↑                     ↓
       └─────── Results + PDF ────────┘
```

## Tech Stack

- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Backend**: Node.js + Express
- **Database**: MongoDB
- **API Client**: Axios
- **Authentication**: JWT (Email/Password)

## Prerequisites

1. **MongoDB** - Install and run MongoDB locally:
   ```bash
   # macOS (using Homebrew)
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community

   # Ubuntu/Debian
   sudo apt-get install mongodb

   # Or use MongoDB Atlas (cloud) for free
   ```

2. **Node.js** - Version 18 or higher

3. **FastAPI ML Service** - Must be running on `http://localhost:5001`

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env and configure:
# MONGODB_URI=mongodb://localhost:27017/hospital-ai
# JWT_SECRET=your-secure-secret-key
# PORT=5000
# FASTAPI_URL=http://localhost:5001

# Start the backend server
npm start
```

The backend will run on `http://localhost:5000`

### 2. Frontend Setup

```bash
# From the root directory
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:5173`

### 3. Verify FastAPI Service

Ensure your FastAPI ML service is running on `http://localhost:5001` and accepts:

**Endpoint**: `POST /process-report`

**Request**:
- Content-Type: `multipart/form-data`
- Field: `file` (PDF file)

**Response**:
```json
{
  "prediction": "Moderate DR",
  "confidence": 0.91,
  "output_pdf": "reports/AI_Report_123.pdf"
}
```

## Usage

1. **Register/Login**: Create an account or sign in
2. **Upload Report**: Select and upload a medical report PDF
3. **View Results**: See AI prediction and confidence score
4. **Download**: Download the AI-generated diagnostic PDF
5. **History**: View all analyzed reports (hospital-wide access)

## Database Schema

### User Collection
```javascript
{
  email: String (unique),
  password: String (hashed),
  createdAt: Date
}
```

### Report Collection
```javascript
{
  original_filename: String,
  prediction: String,
  confidence: Number,
  output_pdf: String,
  createdAt: Date
}
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Reports
- `POST /api/reports/upload` - Upload and analyze report
- `GET /api/reports/history` - Get all reports
- `GET /api/reports/download/:id` - Download report PDF

## Project Structure

```
/
├── backend/
│   ├── models/
│   │   ├── User.js
│   │   └── Report.js
│   ├── routes/
│   │   ├── auth.js
│   │   └── reports.js
│   ├── middleware/
│   │   └── auth.js
│   ├── server.js
│   └── package.json
├── src/
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── Dashboard.jsx
│   ├── components/
│   │   ├── UploadSection.jsx
│   │   └── ReportHistory.jsx
│   ├── services/
│   │   └── api.js
│   └── App.tsx
└── package.json
```

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Protected API routes
- CORS enabled
- Token validation middleware

## Production Deployment

1. Set strong `JWT_SECRET` in production
2. Use MongoDB Atlas for cloud database
3. Configure CORS for your production domain
4. Use environment variables for all sensitive data
5. Enable HTTPS
6. Set up proper error logging

## Troubleshooting

**MongoDB Connection Failed**:
- Ensure MongoDB is running: `brew services list` or `sudo service mongodb status`
- Check connection string in `.env`

**FastAPI Connection Failed**:
- Verify FastAPI is running on port 5001
- Check FASTAPI_URL in backend `.env`

**CORS Errors**:
- Backend CORS is configured for all origins in development
- Adjust in production as needed

## License

MIT
