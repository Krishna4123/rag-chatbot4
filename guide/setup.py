"""
Setup script for RAG Medical Chatbot
Helps users configure the environment and dependencies
"""

import os
import subprocess
import sys

def create_env_file():
    """Create .env file from template"""
    env_content = """# Required API Keys
PINECONE_API_KEY=your_pinecone_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional Configuration
PINECONE_INDEX=career-rag-index
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
OPENROUTER_MODEL=openrouter/auto
PDF_STORAGE_DIR=storage/pdfs
BACKEND_URL=http://localhost:8000
PORT=8000
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️ .env file already exists")

def install_dependencies():
    """Install required Python packages"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['storage', 'storage/pdfs', 'services']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Created necessary directories")

def main():
    """Main setup function"""
    print("🚀 Setting up RAG Medical Chatbot...")
    print()
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed. Please install dependencies manually.")
        return
    
    print()
    print("🎉 Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Get Pinecone API key from: https://pinecone.io")
    print("3. Get OpenRouter API key from: https://openrouter.ai")
    print("4. Run the application:")
    print("   - Backend: python app.py")
    print("   - Frontend: streamlit run streamlit_app.py")
    print()
    print("⚠️  Medical Disclaimer: This chatbot is for informational purposes only.")
    print("   Always consult healthcare professionals for medical advice.")
    print()
    print("For detailed instructions, see README.md")

if __name__ == "__main__":
    main()
