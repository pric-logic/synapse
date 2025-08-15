#!/usr/bin/env python3
"""
Simple installation script for Project Synapse Gemini migration
This script installs the essential packages needed to run the project
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def install_packages():
    """Install required packages"""
    print("🚀 Installing Project Synapse Gemini dependencies...")
    print("=" * 60)
    
    # Step 1: Upgrade pip
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Pip upgrade failed, continuing anyway...")
    
    # Step 2: Install core packages individually to avoid conflicts
    packages = [
        ("google-generativeai==0.7.0", "Google Gemini AI library"),
        ("fastapi==0.104.0", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic==2.5.0", "Data validation"),
        ("python-dotenv", "Environment variable management"),
        ("Pillow", "Image processing")
    ]
    
    failed_packages = []
    
    for package, description in packages:
        if not run_command(f"pip install {package}", f"Installing {description}"):
            failed_packages.append(package)
    
    # Step 3: Report results
    print("\n" + "=" * 60)
    if not failed_packages:
        print("🎉 All packages installed successfully!")
        print("\nNext steps:")
        print("1. Copy env_template.txt to .env")
        print("2. Add your Gemini API key to .env")
        print("3. Run: python test_gemini_migration.py")
        print("4. Start the app: python main.py")
    else:
        print(f"⚠️  Some packages failed to install: {', '.join(failed_packages)}")
        print("\nTroubleshooting:")
        print("1. Try installing failed packages individually:")
        for package in failed_packages:
            print(f"   pip install {package}")
        print("2. Check your Python version (3.8+ required)")
        print("3. Try using a virtual environment")
        print("4. Check your internet connection")
    
    return len(failed_packages) == 0

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env') and os.path.exists('env_template.txt'):
        print("\n📋 Creating .env file from template...")
        try:
            with open('env_template.txt', 'r') as f:
                template = f.read()
            
            with open('.env', 'w') as f:
                f.write(template)
            
            print("✅ .env file created successfully!")
            print("⚠️  IMPORTANT: Edit .env file and add your Gemini API key!")
            print("   Get your API key from: https://makersuite.google.com/app/apikey")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    return True

def main():
    """Main installation function"""
    print("🚀 PROJECT SYNAPSE - GEMINI 2.0 FLASH MIGRATION INSTALLER")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        sys.exit(1)
    
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
    
    # Install packages
    success = install_packages()
    
    # Create .env file
    create_env_file()
    
    # Final instructions
    print("\n" + "=" * 60)
    if success:
        print("🎉 Installation completed successfully!")
        print("\nTo test the installation, run:")
        print("  python test_gemini_migration.py")
    else:
        print("⚠️  Installation completed with some errors.")
        print("Please resolve the failed packages before proceeding.")
    
    print("\nFor help, see MIGRATION_GUIDE.md")

if __name__ == "__main__":
    main()
