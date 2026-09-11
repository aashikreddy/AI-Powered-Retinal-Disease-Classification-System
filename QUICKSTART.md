# Quick Start Guide

Get the Hospital AI System running in 3 steps!

## Prerequisites

1. **MongoDB running** on `localhost:27017`
2. **FastAPI ML service running** on `localhost:5001`
3. **Node.js 18+** installed

## Option 1: Automatic Start (Recommended)

### macOS/Linux
```bash
./start.sh
```

### Windows
```bash
start.bat
```

This will start both backend and frontend automatically.

## Option 2: Manual Start

### Terminal 1 - Backend
```bash
cd backend
npm start
```

Wait for: `✓ MongoDB connected` and `✓ Server running on port 5000`

### Terminal 2 - Frontend
```bash
npm run dev
```

Wait for: `Local: http://localhost:5173/`

## Access the Application

Open browser: **http://localhost:5173**

## First Time Usage

1. **Register**: Click "Register" and create an account
2. **Upload**: Select a PDF medical report and click "Upload & Analyze"
3. **View**: See prediction results and confidence score
4. **Download**: Click download to get the AI-generated report

## Troubleshooting

### MongoDB Not Running
```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongodb

# Windows
net start MongoDB
```

### Port Already in Use
Change PORT in `backend/.env` if 5000 is taken.

### FastAPI Not Responding
Ensure your FastAPI service is running on port 5001:
```bash
curl http://localhost:5001/docs
```

## Default Configuration

- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:5173
- **Database**: mongodb://localhost:27017/hospital-ai
- **FastAPI**: http://localhost:5001

## What's Included

### Backend Features
- User authentication (JWT)
- PDF upload handling
- FastAPI integration
- Report history management
- Secure password hashing

### Frontend Features
- Professional hospital UI (white/blue theme)
- Login/Register pages
- Dashboard with upload
- Real-time upload progress
- Report history table
- PDF download capability

### Security
- JWT token authentication
- Password hashing with bcrypt
- Protected API routes
- CORS configured

## Need Help?

See detailed documentation:
- [Complete Setup Guide](SETUP.md)
- [Backend Documentation](backend/README.md)
- [Main README](README.md)

## Project Structure

```
Hospital-AI-System/
├── backend/              # Node.js + Express API
│   ├── models/          # MongoDB schemas
│   ├── routes/          # API endpoints
│   ├── middleware/      # Auth middleware
│   └── server.js        # Main server
├── src/                 # React frontend
│   ├── pages/          # Login, Register, Dashboard
│   ├── components/     # Upload, History components
│   └── services/       # API integration
└── dist/               # Production build
```

Enjoy your Hospital AI System!
