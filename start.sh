#!/bin/bash

echo "========================================="
echo "Hospital AI System - Startup Script"
echo "========================================="
echo ""

echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✓ Node.js $(node --version) found"

if ! command -v mongod &> /dev/null && ! pgrep -x mongod > /dev/null; then
    echo "⚠️  Warning: MongoDB may not be installed or running"
    echo "   Please ensure MongoDB is running on localhost:27017"
else
    echo "✓ MongoDB found"
fi

echo ""
echo "Checking backend configuration..."

if [ ! -f "backend/.env" ]; then
    echo "❌ Backend .env file not found!"
    echo "Creating from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration"
    echo "   Run: nano backend/.env"
    exit 1
fi

echo "✓ Backend .env exists"
echo ""

echo "Starting services..."
echo ""

echo "Starting Backend (Port 5002)..."
cd backend
npm start &
BACKEND_PID=$!
cd ..

sleep 3

echo "Starting Frontend (Port 5173)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "✓ Services started successfully!"
echo "========================================="
echo ""
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
