#!/usr/bin/env python3
"""
Robot AI Brain - Quick Start Script
Starts both Flask backend and Streamlit frontend
"""

import subprocess
import time
import sys
import os

def main():
    print("\n" + "="*70)
    print("  🤖 ROBOT AI BRAIN - STARTING SYSTEM")
    print("="*70 + "\n")
    
    # Change to project directory
    os.chdir(r"c:\Users\sriha\OneDrive\Pictures\VR 47 2")
    
    print("Step 1️⃣: Starting Flask Backend (Port 5000)...")
    print("-" * 70)
    print("  Opening: python backend.py")
    print("  Expected: Server running on http://localhost:5000")
    print()
    
    # Start backend
    backend_process = subprocess.Popen(
        [sys.executable, 'backend.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("✓ Backend process started (PID: {})".format(backend_process.pid))
    
    # Wait for backend to be ready
    time.sleep(3)
    
    print("\nStep 2️⃣: Starting Streamlit Dashboard (Port 8501)...")
    print("-" * 70)
    print("  Opening: streamlit run app.py")
    print("  Expected: Browser opens at http://localhost:8501")
    print()
    
    # Start Streamlit
    try:
        subprocess.run(
            [sys.executable, '-m', 'streamlit', 'run', 'app.py', '--logger.level=error'],
            check=False
        )
    except KeyboardInterrupt:
        print("\n\n⛔ Shutting down...")
        backend_process.terminate()
        backend_process.wait()
        print("✓ Shutdown complete")
        sys.exit(0)

if __name__ == '__main__':
    main()
