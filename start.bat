@echo off
echo =========================================
echo Hospital AI System - Startup Script
echo =========================================
echo.

echo Checking prerequisites...

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

echo √ Node.js found
echo.

echo Checking backend configuration...

if not exist "backend\.env" (
    echo X Backend .env file not found!
    echo Creating from .env.example...
    copy backend\.env.example backend\.env
    echo ! Please edit backend\.env with your configuration
    exit /b 1
)

echo √ Backend .env exists
echo.

echo Starting services...
echo.

echo Starting Backend (Port 5000)...
start "Hospital AI Backend" cmd /k "cd backend && npm start"

timeout /t 3 /nobreak >nul

echo Starting Frontend (Port 5173)...
start "Hospital AI Frontend" cmd /k "npm run dev"

echo.
echo =========================================
echo √ Services started successfully!
echo =========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Close the terminal windows to stop services
echo.

pause
