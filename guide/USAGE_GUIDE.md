# RAG Medical Chatbot - Usage Guide

## How to Use the System

### 1. Pre-storing PDFs in Storage Folder

The system is designed to automatically process PDFs placed in the `storage/pdfs/` folder:

1. **Place your medical PDFs** in the `storage/pdfs/` directory
2. **Start the backend** - it will automatically process all PDFs on startup
3. **Start the frontend** - you'll see the processed documents in the UI

### 2. Automatic Processing

When you start the Flask backend (`python app.py`), it will:
- Scan the `storage/pdfs/` folder for PDF files
- Extract text from each PDF
- Chunk the text into manageable pieces
- Generate embeddings for each chunk
- Store everything in the Pinecone vector database

### 3. Smart Response System

The chatbot uses a two-tier approach:

#### Tier 1: Document-Based Responses
- When you ask a question, it searches your uploaded PDFs
- If it finds sufficient relevant information, it answers based on your documents
- Shows source citations from your PDFs

#### Tier 2: AI Knowledge Base Fallback
- If there's insufficient relevant data in your PDFs
- The system automatically switches to OpenRouter's medical knowledge base
- Provides comprehensive answers based on general medical knowledge
- Clearly indicates when using AI knowledge vs. your documents

### 4. Example Workflow

1. **Prepare Documents:**
   ```
   storage/pdfs/
   ├── diabetes_guide.pdf
   ├── heart_disease_research.pdf
   └── medication_handbook.pdf
   ```

2. **Start the System:**
   ```bash
   # Terminal 1 - Backend
   python app.py
   
   # Terminal 2 - Frontend  
   streamlit run streamlit_app.py
   ```

3. **Ask Questions:**
   - "What are the symptoms of diabetes?" → Uses your diabetes_guide.pdf
   - "How do I manage blood pressure?" → Uses your heart_disease_research.pdf
   - "What are the side effects of aspirin?" → Uses your medication_handbook.pdf
   - "What is the treatment for pneumonia?" → Falls back to AI knowledge base

### 5. Data Source Indicators

The UI clearly shows the source of each answer:
- 📄 **Answer based on uploaded documents** - Using your PDFs
- 🧠 **Answer based on AI knowledge base** - Using OpenRouter
- ℹ️ **Using AI knowledge base as fallback** - When PDF data is insufficient

### 6. Managing Documents

- **Add new PDFs:** Simply place them in `storage/pdfs/` and click "Reprocess Storage PDFs"
- **Remove PDFs:** Delete files from `storage/pdfs/` and reprocess
- **View statistics:** See how many PDFs are processed and their total size

### 7. Persona Selection

Choose your preferred AI assistant style:
- **👨‍⚕️ Medical Doctor:** Knowledgeable and caring guidance
- **🔬 Medical Specialist:** Technical and research-based information  
- **👩‍⚕️ Registered Nurse:** Compassionate and patient-centered guidance

### 8. Important Notes

- **Medical Disclaimer:** All responses are for informational purposes only
- **Professional Consultation:** Always consult healthcare professionals for medical advice
- **Emergency Situations:** Contact emergency services for urgent medical issues
- **Document Quality:** Use well-formatted PDFs with clear text for best results

### 9. Troubleshooting

- **No PDFs processed:** Check that files are in `storage/pdfs/` and are valid PDFs
- **Poor responses:** Ensure PDFs contain relevant medical information
- **API errors:** Verify your Pinecone and OpenRouter API keys are correct
- **Reprocessing:** Use the "Reprocess Storage PDFs" button to refresh the system

This system provides the best of both worlds: personalized responses based on your specific medical documents, with comprehensive AI knowledge as a reliable fallback.
