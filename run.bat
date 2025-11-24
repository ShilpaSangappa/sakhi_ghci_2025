@echo off
REM Quick start script for Sakhi App (Windows)

echo.
echo ========================================
echo   Sakhi - Your Health Companion
echo   Starting Application...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\activate
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if backend database exists
if not exist "data\sakhi.db" (
    echo [INFO] Database not found. Initializing...
    cd backend
    python database.py
    cd ..
    echo.
)

REM Start backend in new window
echo [INFO] Starting backend server...
start "Sakhi Backend" cmd /k "venv\Scripts\activate && cd backend && python main.py"

REM Wait for backend to start
echo [INFO] Waiting for backend to start...
timeout /t 5 /nobreak > nul

REM Start frontend
echo [INFO] Starting frontend app...
cd frontend
python main.py

echo.
echo ========================================
echo   Application closed
echo ========================================
pause
