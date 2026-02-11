#!/usr/bin/env python3
"""
Robot AI Brain - Complete Setup & Test Script
Verifies all dependencies and starts both backend and Streamlit
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_banner():
    print("\n" + "="*70)
    print("  🤖 ROBOT AI BRAIN - SETUP & TEST")
    print("="*70 + "\n")

def check_python():
    """Verify Python version"""
    print("✓ Python version:", sys.version.split()[0])
    if sys.version_info < (3, 7):
        print("✗ ERROR: Python 3.7+ required")
        sys.exit(1)

def check_dependencies():
    """Verify all required packages are installed"""
    print("\n📦 Checking dependencies...")
    required = ['flask', 'flask_cors', 'requests', 'streamlit']
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} NOT INSTALLED")
            print(f"\n  Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', package])
            print(f"  ✓ {package} installed")

def check_files():
    """Verify all required files exist"""
    print("\n📁 Checking project files...")
    required_files = [
        'app.py',
        'backend.py',
        'robot_brain.py',
        'config.py',
        'requirements.txt'
    ]
    
    current_dir = Path.cwd()
    for file in required_files:
        path = current_dir / file
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {file} ({size} bytes)")
        else:
            print(f"  ✗ {file} NOT FOUND")
            sys.exit(1)

def test_backend_import():
    """Test if backend can be imported"""
    print("\n🔧 Testing backend module...")
    try:
        import backend
        print("  ✓ Backend module imports successfully")
    except Exception as e:
        print(f"  ✗ Backend error: {e}")
        sys.exit(1)

def test_robot_brain():
    """Test if robot brain can be imported"""
    print("\n🧠 Testing robot brain module...")
    try:
        from robot_brain import RobotBrain, ExpertResponder
        brain = RobotBrain()
        print("  ✓ Robot brain initialized successfully")
        
        # Test decision logic
        brain.add_sensor_reading(45.0, 60.0, 55.0)
        decision = brain.decide_navigation(45.0, 60.0, 55.0, 50.0, 100.0)
        print(f"  ✓ Decision logic working: {decision['decision']}")
    except Exception as e:
        print(f"  ✗ Robot brain error: {e}")
        sys.exit(1)

def print_startup_guide():
    """Print how to start the system"""
    print("\n" + "="*70)
    print("  ✅ ALL CHECKS PASSED - System Ready!")
    print("="*70)
    
    print("\n📖 HOW TO RUN:\n")
    print("  STEP 1 - Start Backend Server (Terminal 1):")
    print("  " + "-"*60)
    print("    cd \"c:\\Users\\sriha\\OneDrive\\Pictures\\VR 47 2\"")
    print("    python backend.py")
    print("\n  Expected output:")
    print("    * API server on 0.0.0.0:5000")
    print("    * Ready to receive sensor data")
    
    print("\n  STEP 2 - Start Streamlit UI (Terminal 2):")
    print("  " + "-"*60)
    print("    cd \"c:\\Users\\sriha\\OneDrive\\Pictures\\VR 47 2\"")
    print("    streamlit run app.py")
    print("\n  Expected output:")
    print("    * Opens http://localhost:8501")
    print("    * Shows chatbot dashboard")
    
    print("\n  STEP 3 - Test in Streamlit:")
    print("  " + "-"*60)
    print("    1. Go to sidebar → Click '🔗 Test API Connection'")
    print("    2. Should show: ✓ Connected to Robot AI Brain!")
    print("    3. Go to '🎮 Manual Control' tab")
    print("    4. Click '🚀 Get AI Decision'")
    print("    5. See decision and explanation")
    
    print("\n📱 ACCESS POINTS:")
    print("  " + "-"*60)
    print("    • Streamlit UI:  http://localhost:8501")
    print("    • Flask API:     http://localhost:5000/api/health")
    print("    • API Docs:      http://localhost:5000")
    
    print("\n🤖 FOR YOUR ESP32 ROBOT:")
    print("  " + "-"*60)
    print("    POST http://YOUR_LAPTOP_IP:5000/api/robot/decide")
    print("    Content-Type: application/json")
    print("    Body:")
    print("    {")
    print("        \"front_dist\": 45.2,")
    print("        \"left_dist\": 60.0,")
    print("        \"right_dist\": 35.5,")
    print("        \"encoder_pulses\": 1240")
    print("    }")
    
    print("\n" + "="*70)
    print("  ✨ Ready to Autonomously Navigate! 🚀")
    print("="*70 + "\n")

if __name__ == '__main__':
    print_banner()
    
    print("Running system checks...\n")
    check_python()
    check_dependencies()
    check_files()
    test_backend_import()
    test_robot_brain()
    
    print_startup_guide()
    
    # Ask if user wants to start now
    response = input("Would you like to start the backend server now? (y/n): ")
    if response.lower() == 'y':
        print("\n🚀 Starting Flask backend...")
        subprocess.run([sys.executable, 'backend.py'])
