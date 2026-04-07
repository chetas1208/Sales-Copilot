#!/bin/bash

# Meetstream AI Backend Startup Script

echo "[START] Starting Meetstream AI Backend..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARN] .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "[ERROR] Please edit backend/.env and add your OPENAI_API_KEY before continuing"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[SETUP] Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "[INSTALL] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "[INSTALL] Installing Playwright browsers..."
playwright install chromium

# Run the server
echo "[READY] Starting FastAPI server on http://localhost:8000"
echo "[INFO] WebSocket endpoint: ws://localhost:8000/ws"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
