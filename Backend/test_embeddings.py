#!/usr/bin/env python3
"""
Test script to verify embedding functionality
Run this to check if your GEMINI_API_KEY is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if GEMINI_API_KEY is available"""
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key != 'your_api_key_here':
        print(f"✅ GEMINI_API_KEY found (length: {len(api_key)})")
        return True
    else:
        print("❌ GEMINI_API_KEY not found or not set")
        print("📝 To fix this:")
        print("   1. Copy .env.example to .env")
        print("   2. Get API key from: https://makersuite.google.com/app/apikey")
        print("   3. Replace 'your_api_key_here' with your actual API key")
        return False

def test_embedding_import():
    """Test if required packages are available"""
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print("✅ GoogleGenerativeAIEmbeddings import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_embedding_creation():
    """Test if embedding can be created with API key"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("⚠️  Skipping embedding test - no valid API key")
        return False
    
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        print("✅ Embeddings created successfully")
        
        # Test with a simple text
        test_text = "This is a test document"
        result = embeddings.embed_query(test_text)
        print(f"✅ Embedding test successful (vector length: {len(result)})")
        return True
        
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False

def main():
    print("🔧 Testing Embedding Configuration")
    print("=" * 50)
    
    results = []
    results.append(test_api_key())
    results.append(test_embedding_import())
    
    if results[0]:  # Only test embedding if API key exists
        results.append(test_embedding_creation())
    
    print("\n📊 Test Summary:")
    print("=" * 50)
    
    if all(results):
        print("🎉 All tests passed! Embedding functionality is working.")
        print("✅ Your documents will be stored in vector database.")
    else:
        print("⚠️  Some tests failed. System will use fallback mode.")
        print("📝 Documents will be processed but not stored in vector DB.")
    
    print("\n🚀 To enable full functionality:")
    print("   1. Set up GEMINI_API_KEY in .env file")
    print("   2. Restart the FastAPI server")
    print("   3. Test document upload again")

if __name__ == "__main__":
    main()