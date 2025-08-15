#!/usr/bin/env python3
"""
Test script to verify Gemini migration
Run this script to test if the migration from OpenAI to Gemini was successful
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_configuration():
    """Test if configuration is properly set up"""
    print("🔧 Testing configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please copy env_template.txt to .env and configure your Gemini API key.")
        return False
    
    # Check if Gemini API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY not properly configured in .env file.")
        return False
    
    print("✅ Configuration test passed!")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("📦 Testing imports...")
    
    try:
        import google.generativeai
        print("✅ google.generativeai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        return False
    
    try:
        from config import config
        print("✅ Configuration module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from utils.gemini_client import get_gemini_client
        print("✅ Gemini client module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Gemini client: {e}")
        return False
    
    print("✅ All imports successful!")
    return True

def test_gemini_client():
    """Test if Gemini client can be initialized"""
    print("🤖 Testing Gemini client...")
    
    try:
        from utils.gemini_client import get_gemini_client
        client = get_gemini_client()
        print("✅ Gemini client initialized successfully")
        
        # Test health check
        if client.health_check():
            print("✅ Gemini API health check passed")
        else:
            print("⚠️  Gemini API health check failed")
        
        # Get model info
        model_info = client.get_model_info()
        print(f"✅ Model info retrieved: {model_info.get('current_model', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test Gemini client: {e}")
        return False

def test_text_generation():
    """Test basic text generation"""
    print("📝 Testing text generation...")
    
    try:
        from utils.gemini_client import get_gemini_client
        client = get_gemini_client()
        
        # Simple test prompt
        prompt = "Hello! Please respond with 'Gemini migration successful!'"
        response = client.generate_text(prompt, temperature=0.1, max_tokens=50)
        
        if response and len(response) > 0:
            print(f"✅ Text generation successful: {response[:100]}...")
            return True
        else:
            print("❌ Text generation returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test text generation: {e}")
        return False

def test_system_prompt():
    """Test system prompt functionality"""
    print("🎭 Testing system prompt...")
    
    try:
        from utils.gemini_client import get_gemini_client
        client = get_gemini_client()
        
        system_prompt = "You are a helpful assistant. Always respond with 'SUCCESS'."
        user_prompt = "What should you say?"
        
        response = client.generate_text_with_system_prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1
        )
        
        if response and len(response) > 0:
            print(f"✅ System prompt test successful: {response[:100]}...")
            return True
        else:
            print("❌ System prompt test returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test system prompt: {e}")
        return False

def test_config_module():
    """Test configuration module"""
    print("⚙️  Testing configuration module...")
    
    try:
        from config import config
        
        # Test basic config values
        print(f"   Model: {config.GEMINI_MODEL}")
        print(f"   API Key configured: {bool(config.GEMINI_API_KEY)}")
        print(f"   API Host: {config.API_HOST}")
        print(f"   API Port: {config.API_PORT}")
        
        # Test validation
        if config.validate():
            print("✅ Configuration validation passed")
        else:
            print("⚠️  Configuration validation failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test configuration: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Gemini Migration Tests...")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Imports", test_imports),
        ("Configuration Module", test_config_module),
        ("Gemini Client", test_gemini_client),
        ("Text Generation", test_text_generation),
        ("System Prompt", test_system_prompt),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gemini migration is successful!")
        print("\nNext steps:")
        print("1. Start the application: python main.py")
        print("2. Check Gemini status: curl http://localhost:8000/gemini/info")
        print("3. Run demo scenarios: curl http://localhost:8000/demo/scenarios")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure you have a valid Gemini API key")
        print("2. Check that all dependencies are installed")
        print("3. Verify your .env file configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()
