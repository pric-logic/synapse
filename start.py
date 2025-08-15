#!/usr/bin/env python3
"""
Project Synapse Startup Script
Easily run the application in different modes
"""

import sys
import subprocess
import os
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit', 'fastapi', 'uvicorn', 'pandas', 'plotly',
        'numpy', 'pillow', 'faker'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True


def run_streamlit():
    """Run the Streamlit dashboard"""
    print("🚀 Starting Project Synapse Streamlit Dashboard...")
    print("📱 Dashboard will open in your browser")
    print("🔗 Local URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")


def run_fastapi():
    """Run the FastAPI backend"""
    print("🚀 Starting Project Synapse FastAPI Backend...")
    print("🔗 API URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running FastAPI: {e}")


def run_both():
    """Run both Streamlit and FastAPI"""
    print("🚀 Starting Project Synapse (Full Stack)...")
    print("📱 Dashboard: http://localhost:8501")
    print("🔗 API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        # Start FastAPI in background
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
        
        # Wait a moment for API to start
        import time
        time.sleep(3)
        
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        if 'api_process' in locals():
            api_process.terminate()
            api_process.wait()
        print("✅ All services stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running services: {e}")


def show_help():
    """Show help information"""
    print("""
🚀 PROJECT SYNAPSE - Startup Script

Usage: python start.py [mode]

Modes:
  streamlit    Run Streamlit dashboard only (default)
  fastapi      Run FastAPI backend only
  both         Run both Streamlit and FastAPI
  help         Show this help message

Examples:
  python start.py              # Run Streamlit dashboard
  python start.py fastapi      # Run FastAPI backend
  python start.py both         # Run full stack

Dashboard Features:
  🎪 Demo Scenarios
  🔍 Multimodal Analysis
  💰 Profit Optimization
  🔮 Prediction Engine
  🔌 API Simulator
  📚 History & Learning Demo

For more information, see README.md
""")


def main():
    """Main startup function"""
    print("🚀 PROJECT SYNAPSE")
    print("Multimodal Predictive Delivery Orchestrator")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Get mode from command line arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else "streamlit"
    
    # Run based on mode
    if mode == "streamlit":
        run_streamlit()
    elif mode == "fastapi":
        run_fastapi()
    elif mode == "both":
        run_both()
    elif mode in ["help", "-h", "--help"]:
        show_help()
    else:
        print(f"❌ Unknown mode: {mode}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 