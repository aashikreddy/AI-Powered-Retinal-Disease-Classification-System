# Hospital AI System - Complete Setup Guide

This guide will help you set up the complete Hospital AI system step by step.

## System Overview

The system consists of three main components:

1. **Frontend** (React + Vite) - Port 5173
2. **Backend** (Node.js + Express) - Port 5000
3. **ML Service** (FastAPI) - Port 5001 (Already implemented)

## Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] MongoDB installed and running
- [ ] FastAPI ML service running on port 5001
- [ ] Git (for version control)

## Step-by-Step Setup

### Step 1: Install MongoDB

#### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Verify MongoDB is running
brew services list
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Verify MongoDB is running
sudo systemctl status mongodb
```

#### Windows
Download from: https://www.mongodb.com/try/download/community

Or use MongoDB Atlas (cloud, free tier): https://www.mongodb.com/cloud/atlas

### Step 2: Verify FastAPI Service

Your FastAPI service should be running on `http://localhost:5001`

Test it:
```bash
curl http://localhost:5001/docs
```

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env file (use your preferred editor)
nano .env

# Set these values:
# MONGODB_URI=mongodb://localhost:27017/hospital-ai
# JWT_SECRET=create-a-long-random-secure-key-here
# PORT=5000
# FASTAPI_URL=http://localhost:5001

# Create uploads directory
mkdir -p uploads

# Start the backend
npm start
```

**Expected Output:**
```
✓ MongoDB connected
✓ Server running on port 5000
```

Keep this terminal open.

### Step 4: Frontend Setup

Open a new terminal:

```bash
# Navigate to project root (where package.json is)
cd ..  # if you're in backend/

# Install frontend dependencies
npm install

# Start the development server
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 5: Access the Application

Open your browser and navigate to: **http://localhost:5173**

You should see the Hospital AI System login page.

## Testing the System

### 1. Register a New User

1. Click "Register" on the login page
2. Enter email: `test@hospital.com`
3. Enter password: `test1234`
4. Click "Register"

### 2. Upload a Medical Report

1. You'll be automatically logged in after registration
2. Click "Select PDF File"
3. Choose a medical report PDF
4. Click "Upload & Analyze"
5. Wait for the AI analysis to complete

### 3. View Results

After successful upload, you should see:
- Prediction label
- Confidence percentage
- Download button for AI-generated report

### 4. Check Report History

All analyzed reports appear in the "Report History" table below the upload section.

## Troubleshooting

### MongoDB Connection Error

**Error:** `MongoDB connection error`

**Solution:**
```bash
# Check if MongoDB is running
brew services list  # macOS
sudo systemctl status mongodb  # Linux

# If not running, start it
brew services start mongodb-community  # macOS
sudo systemctl start mongodb  # Linux
```

### Backend Cannot Connect to FastAPI

**Error:** `Failed to process report` or `ECONNREFUSED localhost:5001`

**Solution:**
- Verify FastAPI is running: `curl http://localhost:5001/docs`
- Check FASTAPI_URL in backend/.env
- Ensure FastAPI accepts POST /process-report

### CORS Errors in Browser

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
- Backend should already have CORS enabled
- Check backend console for errors
- Restart backend server

### Port Already in Use

**Error:** `Port 5000 is already in use`

**Solution:**
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows

# Or change PORT in backend/.env
```

## Running Both Services Together

You can use a process manager to run both services:

```bash
# Install concurrently
npm install -g concurrently

# Run from project root
concurrently "cd backend && npm start" "npm run dev"
```

## MongoDB Data

### View Database Contents

```bash
# Connect to MongoDB shell
mongosh

# Switch to database
use hospital-ai

# View users
db.users.find()

# View reports
db.reports.find()

# Exit
exit
```

### Reset Database

```bash
mongosh
use hospital-ai
db.users.deleteMany({})
db.reports.deleteMany({})
exit
```

## Production Deployment

For production deployment:

1. **Backend:**
   - Use MongoDB Atlas (cloud database)
   - Set strong JWT_SECRET
   - Configure CORS for your domain
   - Use PM2 for process management
   - Enable HTTPS

2. **Frontend:**
   - Update API_BASE_URL in src/services/api.js
   - Build: `npm run build`
   - Serve dist/ folder with nginx or similar

## Support

If you encounter issues:

1. Check all services are running (MongoDB, Backend, Frontend, FastAPI)
2. Verify environment variables in backend/.env
3. Check browser console for errors
4. Check backend terminal for error logs
5. Ensure all ports are available (5000, 5001, 5173)

## Next Steps

After successful setup:

1. Test all features thoroughly
2. Add more users
3. Upload multiple reports
4. Test download functionality
5. Customize styling if needed
6. Add additional features as required

Enjoy your Hospital AI System!
