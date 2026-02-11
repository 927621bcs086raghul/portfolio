@echo off
REM Robot AI Brain - Startup Script
REM This script starts both backend and Streamlit UI

echo.
echo ========================================
echo  ROBOT AI BRAIN - Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed. Install from python.org
    pause
    exit /b 1
)

REM Install requirements if not done
echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo ========================================
echo Starting Backend Server (Port 5000)...
echo ========================================
echo.

REM Start backend in background
start "Robot AI Backend" python backend.py

REM Wait for backend to start
timeout /t 3 /nobreak

echo.
echo ========================================
echo Starting Streamlit UI (Port 8501)...
echo ========================================
echo.

REM Start Streamlit
streamlit run app.py

pause
