#!/usr/bin/env python3
"""
Quick Start Script for Project Synapse (Gemini Edition)
This script helps you get the project running quickly after migration
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print the project banner"""
    print("🚀" * 20)
    print("🚀 PROJECT SYNAPSE - GEMINI 2.0 FLASH EDITION 🚀")
    print("🚀" * 20)
    print("Multimodal Predictive Delivery Orchestrator")
    print("Powered by Google Gemini 2.0 Flash AI")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'google.generativeai',
        'fastapi',
        'uvicorn',
        'pydantic',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('.', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Try one of these solutions:")
        print("1. pip install -r requirements_simple.txt")
        print("2. pip install google-generativeai==0.7.0 fastapi uvicorn pydantic python-dotenv Pillow")
        print("3. If you encounter conflicts, install packages individually")
        return False
    
    print("✅ All required packages are installed")
    return True

def setup_environment():
    """Set up environment configuration"""
    print("⚙️  Setting up environment...")
    
    env_file = Path('.env')
    template_file = Path('env_template.txt')
    
    if not env_file.exists():
        if template_file.exists():
            print("📋 Creating .env file from template...")
            try:
                with open(template_file, 'r') as f:
                    template_content = f.read()
                
                with open(env_file, 'w') as f:
                    f.write(template_content)
                
                print("✅ .env file created from template")
                print("⚠️  IMPORTANT: Edit .env file and add your Gemini API key!")
                print("   Get your API key from: https://makersuite.google.com/app/apikey")
                return False
            except Exception as e:
                print(f"❌ Failed to create .env file: {e}")
                return False
        else:
            print("❌ env_template.txt not found")
            return False
    else:
        print("✅ .env file already exists")
        
        # Check if API key is configured
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key or api_key == 'your_gemini_api_key_here':
                print("⚠️  GEMINI_API_KEY not configured in .env file")
                print("   Edit .env file and add your Gemini API key")
                return False
            
            print("✅ Gemini API key is configured")
            return True
            
        except Exception as e:
            print(f"❌ Error checking .env file: {e}")
            return False

def run_tests():
    """Run migration tests"""
    print("🧪 Running migration tests...")
    
    if not os.path.exists('test_gemini_migration.py'):
        print("❌ test_gemini_migration.py not found")
        return False
    
    try:
        result = subprocess.run([sys.executable, 'test_gemini_migration.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def start_application():
    """Start the application"""
    print("🚀 Starting Project Synapse...")
    
    try:
        # Start the application in the background
        process = subprocess.Popen([sys.executable, 'main.py'])
        
        print("✅ Application started successfully!")
        print(f"🌐 API available at: http://localhost:8000")
        print(f"📚 API documentation: http://localhost:8000/docs")
        print(f"🔍 Health check: http://localhost:8000/health")
        print(f"🤖 Gemini status: http://localhost:8000/gemini/info")
        print()
        print("Press Ctrl+C to stop the application")
        
        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping application...")
            process.terminate()
            process.wait()
            print("✅ Application stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def main():
    """Main quick start function"""
    print_banner()
    
    print("This script will help you get Project Synapse running with Gemini AI.")
    print()
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and run this script again.")
        sys.exit(1)
    
    print()
    
    # Step 3: Setup environment
    if not setup_environment():
        print("\nPlease configure your .env file and run this script again.")
        sys.exit(1)
    
    print()
    
    # Step 4: Run tests
    if not run_tests():
        print("\nMigration tests failed. Please check the errors above.")
        sys.exit(1)
    
    print()
    
    # Step 5: Start application
    print("🎉 All checks passed! Ready to start the application.")
    print()
    
    response = input("Would you like to start the application now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        start_application()
    else:
        print("\nTo start the application manually, run:")
        print("  python main.py")
        print("\nOr for development mode:")
        print("  uvicorn main:app --reload")

if __name__ == "__main__":
    main()
