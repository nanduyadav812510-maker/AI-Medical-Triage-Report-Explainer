#!/usr/bin/env python
"""
Unified launcher for AI Medical Triage application.
Starts both FastAPI backend and Streamlit frontend in a single command.
"""

import subprocess
import time
import webbrowser
import os
import sys
from pathlib import Path

def main():
    """Start both backend and frontend servers."""
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("=" * 60)
    print("🏥 AI Medical Triage - Unified Launcher")
    print("=" * 60)
    
    # Start FastAPI backend
    print("\n📡 Starting Backend API (FastAPI)...")
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Backend starting on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return 1
    
    # Wait for backend to be ready
    time.sleep(3)
    
    # Start Streamlit frontend
    print("\n🎨 Starting Frontend (Streamlit)...")
    try:
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--logger.level=warning"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Frontend starting on http://localhost:8501")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        backend_process.terminate()
        return 1
    
    # Wait for Streamlit to be ready
    time.sleep(5)
    
    # Open browser to frontend
    print("\n🌐 Opening application in browser...")
    try:
        webbrowser.open("http://localhost:8501")
        print("✅ Browser opened!")
    except:
        print("⚠️  Could not open browser automatically.")
        print("   Open manually: http://localhost:8501")
    
    print("\n" + "=" * 60)
    print("✅ Both services running!")
    print("=" * 60)
    print("\n📌 Access Points:")
    print("   Frontend (UI):  http://localhost:8501")
    print("   Backend (API):  http://localhost:8000")
    print("   API Docs:       http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop all services")
    print("=" * 60 + "\n")
    
    try:
        # Keep the script running
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for graceful shutdown
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ All services stopped")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
