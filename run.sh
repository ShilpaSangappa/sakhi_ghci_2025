#!/bin/bash
# Quick start script for Sakhi App (Linux/Mac)

echo ""
echo "========================================"
echo "  Sakhi - Your Health Companion"
echo "  Starting Application..."
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    echo "Then run: source venv/bin/activate"
    echo "Then run: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if backend database exists
if [ ! -f "data/sakhi.db" ]; then
    echo "[INFO] Database not found. Initializing..."
    cd backend
    python database.py
    cd ..
    echo ""
fi

# Start backend in background
echo "[INFO] Starting backend server..."
cd backend
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "[INFO] Waiting for backend to start..."
sleep 5

# Start frontend
echo "[INFO] Starting frontend app..."
cd frontend
python main.py

# Cleanup: Kill backend when frontend closes
echo ""
echo "[INFO] Stopping backend server..."
kill $BACKEND_PID 2>/dev/null

echo ""
echo "========================================"
echo "  Application closed"
echo "========================================"
