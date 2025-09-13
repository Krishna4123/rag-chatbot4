# RAG Medical Chatbot

A comprehensive Retrieval-Augmented Generation (RAG) medical guidance chatbot that ingests PDFs, generates embeddings, stores vectors in Pinecone, and provides personalized medical information through a Streamlit interface.

## 🚀 Features

- **PDF Document Processing**: Upload and process medical-related PDF documents
- **Intelligent Text Chunking**: Token-aware text segmentation with overlap
- **Vector Storage**: Pinecone integration for efficient similarity search
- **Multiple AI Personas**: Choose between Doctor, Specialist, or Nurse styles
- **Source Citations**: Every response includes source references
- **Interactive Chat Interface**: Clean, modern Streamlit UI
- **Namespace Support**: Organize different document sets
- **Medical Disclaimer**: Clear warnings about informational use only

## 📁 Project Structure

```
RagchatBot/
├── app.py                    # Flask backend entry point
├── streamlit_app.py          # Streamlit frontend
├── requirements.txt          # Python dependencies
├── setup.py                  # Setup automation script
├── test_setup.py            # Setup verification script
├── README.md                # This file
├── services/                 # Backend services
│   ├── __init__.py
│   ├── pdf_ingest.py        # PDF text extraction
│   ├── chunker.py           # Token-aware text chunking
│   ├── embeddings.py        # Hugging Face embeddings
│   ├── vector_store.py      # Pinecone vector operations
│   └── rag.py               # RAG orchestration
└── storage/
    └── pdfs/                # PDF storage directory
```

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Pinecone account and API key
- OpenRouter account and API key

### 2. Environment Setup

```bash
# Clone or download the project
cd RagchatBot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. API Keys Configuration

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required API Keys
PINECONE_API_KEY=your_pinecone_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional Configuration
PINECONE_INDEX=career-rag-index
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
OPENROUTER_MODEL=openrouter/auto
PDF_STORAGE_DIR=storage/pdfs
BACKEND_URL=http://localhost:8000
PORT=8000
```

### 4. Get API Keys

#### Pinecone API Key
1. Visit [pinecone.io](https://pinecone.io)
2. Create a free account
3. Go to API Keys section
4. Copy your API key

#### OpenRouter API Key
1. Visit [openrouter.ai](https://openrouter.ai)
2. Create an account
3. Go to API Keys section
4. Generate a new API key

### 5. Run the Application

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
python app.py
```

**Terminal 2 - Frontend:**
```bash
streamlit run streamlit_app.py
```

The application will be available at:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000

## 🎯 Usage

### 1. Upload Documents
- Use the sidebar to upload PDF files containing medical information
- Documents are automatically processed and chunked
- Each document is stored with metadata in `storage/pdfs/`

### 2. Choose AI Persona
- **Medical Doctor**: Knowledgeable and caring medical guidance
- **Medical Specialist**: Technical and research-based information
- **Registered Nurse**: Compassionate and patient-centered guidance

### 3. Ask Questions
- Type medical and health questions in the chat
- Get personalized responses with source citations
- View relevance scores for retrieved information

### 4. Manage Data
- Use namespaces to organize different document sets
- Clear data when needed
- View statistics about uploaded documents

## 🔧 Technical Details

### Chunking Strategy
- **Size**: 300-500 tokens per chunk
- **Overlap**: 20% between consecutive chunks
- **Tokenizer**: tiktoken (cl100k_base)

### Embeddings
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimensions**: 384
- **Similarity**: Cosine similarity

### Vector Store
- **Provider**: Pinecone
- **Index Type**: Serverless (AWS us-east-1)
- **Metric**: Cosine similarity
- **Retrieval**: Top 8 chunks per query

### LLM Integration
- **Provider**: OpenRouter
- **Default Model**: openrouter/auto
- **Temperature**: 0.3
- **Context Window**: Handles retrieved chunks

## 🚨 Troubleshooting

### Common Issues

1. **Backend not running**
   - Ensure Flask server is running on port 8000
   - Check for port conflicts

2. **API key errors**
   - Verify API keys in `.env` file
   - Check API key permissions

3. **PDF processing fails**
   - Ensure PDF files are not corrupted
   - Check file size limits (16MB max)

4. **No responses from AI**
   - Verify OpenRouter API key
   - Check internet connection
   - Ensure documents are uploaded

### Debug Mode

Run with debug information:
```bash
# Backend with debug
FLASK_DEBUG=1 python app.py

# Frontend with debug
streamlit run streamlit_app.py --logger.level=debug
```

## 📊 Performance Tips

1. **Document Quality**: Use well-formatted medical PDFs with clear text
2. **Chunk Size**: Adjust chunk size based on document type
3. **Batch Processing**: Upload multiple documents at once
4. **Namespace Organization**: Use namespaces for different medical topics

## ⚠️ Medical Disclaimer

**IMPORTANT**: This chatbot is for informational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns. In case of medical emergencies, contact emergency services immediately.

## 🔒 Security Notes

- API keys are stored in environment variables only
- No hardcoded credentials in the code
- File uploads are validated for type and size
- Input validation on all API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify API keys are correct

## 🔄 Updates

To update the application:
1. Pull the latest changes
2. Update dependencies: `pip install -r requirements.txt`
3. Restart both backend and frontend servers

---

**Stay healthy and informed! 🏥**
