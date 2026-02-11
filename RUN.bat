@echo off
REM =============================================================
REM  ROBOT AI BRAIN - COMPLETE STARTUP SCRIPT
REM =============================================================

echo.
echo ===============================================================
echo   ROBOT AI BRAIN - Autonomous Navigation System
echo ===============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install -q flask flask-cors requests streamlit
if errorlevel 1 (
    echo ERROR: Dependency installation failed
    pause
    exit /b 1
)
echo      ✓ Dependencies ready

echo.
echo [2/3] Starting Backend Server (Port 5000)...
echo      Opening new window for backend...
start "Robot AI Backend" cmd /k python backend.py

echo      Waiting for backend to start...
timeout /t 3 /nobreak

echo.
echo [3/3] Starting Streamlit UI (Port 8501)...
echo.
echo ===============================================================
echo   LAUNCHING DASHBOARD...
echo ===============================================================
echo.
streamlit run app.py --logger.level=error

pause
