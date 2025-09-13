"""
Test script to verify RAG Medical Chatbot setup
Checks dependencies, API keys, and basic functionality
"""

import os
import sys
import importlib
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'flask',
        'flask_cors',
        'streamlit',
        'PyPDF2',
        'sentence_transformers',
        'pinecone',
        'tiktoken',
        'requests',
        'dotenv'
    ]
    
    print("🔍 Testing package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing packages: pip install -r requirements.txt")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_env_variables():
    """Test if environment variables are set"""
    load_dotenv()
    
    print("\n🔍 Testing environment variables...")
    
    required_vars = ['PINECONE_API_KEY', 'OPENROUTER_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f'your_{var.lower()}_here':
            print(f"  ❌ {var}: Not set or using placeholder")
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: Set")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please edit .env file with your actual API keys")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_services():
    """Test if services can be initialized"""
    print("\n🔍 Testing service initialization...")
    
    try:
        from services.pdf_ingest import PDFProcessor
        from services.chunker import TextChunker
        from services.embeddings import EmbeddingService
        
        # Test PDF processor
        pdf_processor = PDFProcessor()
        print("  ✅ PDFProcessor")
        
        # Test chunker
        chunker = TextChunker()
        print("  ✅ TextChunker")
        
        # Test embeddings (this might take a moment)
        print("  ⏳ Loading embedding model...")
        embedding_service = EmbeddingService()
        print("  ✅ EmbeddingService")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service initialization failed: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    print("\n🔍 Testing directory structure...")
    
    required_dirs = ['services', 'storage', 'storage/pdfs']
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/: Missing")
            return False
    
    print("✅ All required directories exist")
    return True

def main():
    """Run all tests"""
    print("🧪 RAG Medical Chatbot Setup Test")
    print("=" * 40)
    
    tests = [
        test_directories,
        test_imports,
        test_env_variables,
        test_services
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo run the application:")
        print("1. Backend: python app.py")
        print("2. Frontend: streamlit run streamlit_app.py")
        print("\n⚠️  Medical Disclaimer: This chatbot is for informational purposes only.")
        print("   Always consult healthcare professionals for medical advice.")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nFor help, see README.md or run: python setup.py")

if __name__ == "__main__":
    main()
