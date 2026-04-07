@echo off
REM Meetstream AI Backend Startup Script for Windows

echo Starting Meetstream AI Backend...

REM Check if .env file exists
if not exist ".env" (
    echo .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Please edit backend\.env and add your OPENAI_API_KEY before continuing
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

REM Run the server
echo Starting FastAPI server on http://localhost:8000
echo WebSocket endpoint: ws://localhost:8000/ws
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
