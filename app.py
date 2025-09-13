"""
Flask backend for RAG Medical Chatbot
Handles PDF ingestion, vector operations, and medical chat queries
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from services.pdf_ingest import PDFProcessor
from services.chunker import TextChunker
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.rag import RAGService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.getenv('PDF_STORAGE_DIR', 'storage/pdfs')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize services
pdf_processor = PDFProcessor()
chunker = TextChunker()
embedding_service = EmbeddingService()
vector_store = VectorStore()
rag_service = RAGService()

def process_storage_pdfs():
    """Process all PDFs in the storage folder on startup"""
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            return
        
        pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print("No PDFs found in storage folder")
            return
        
        print(f"Found {len(pdf_files)} PDFs in storage folder. Processing...")
        
        for filename in pdf_files:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                # Extract text
                pdf_text = pdf_processor.extract_text(filepath)
                if not pdf_text:
                    print(f"Failed to extract text from {filename}")
                    continue
                
                # Chunk the text
                chunks = chunker.chunk_text(pdf_text, filename)
                
                # Generate embeddings
                embeddings = embedding_service.generate_embeddings([chunk['text'] for chunk in chunks])
                
                # Store in vector database
                vector_store.store_vectors(chunks, embeddings, filename)
                
                print(f"✅ Processed {filename} - {len(chunks)} chunks")
                
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
                continue
        
        print("Storage PDF processing completed!")
        
    except Exception as e:
        print(f"Error processing storage PDFs: {e}")

# Process existing PDFs on startup
process_storage_pdfs()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'RAG Medical Chatbot API is running'
    })

@app.route('/ingest', methods=['POST'])
def ingest_pdf():
    """Upload and process PDF files"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process PDF
        pdf_text = pdf_processor.extract_text(filepath)
        if not pdf_text:
            return jsonify({'error': 'Failed to extract text from PDF'}), 400
        
        # Chunk the text
        chunks = chunker.chunk_text(pdf_text, filename)
        
        # Generate embeddings
        embeddings = embedding_service.generate_embeddings([chunk['text'] for chunk in chunks])
        
        # Store in vector database
        vector_store.store_vectors(chunks, embeddings, filename)
        
        return jsonify({
            'message': f'Successfully processed {filename}',
            'chunks_created': len(chunks),
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat queries with RAG"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        persona = data.get('persona', 'mentor')
        namespace = data.get('namespace', 'default')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get response from RAG service
        response = rag_service.query(query, persona, namespace)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500

@app.route('/admin/clear', methods=['POST'])
def clear_vectors():
    """Clear all vectors from the database"""
    try:
        namespace = request.json.get('namespace', 'default') if request.is_json else 'default'
        vector_store.clear_namespace(namespace)
        return jsonify({'message': f'Cleared vectors in namespace: {namespace}'})
    except Exception as e:
        return jsonify({'error': f'Clear failed: {str(e)}'}), 500

@app.route('/admin/reprocess', methods=['POST'])
def reprocess_storage():
    """Reprocess all PDFs in storage folder"""
    try:
        process_storage_pdfs()
        return jsonify({'message': 'Storage PDFs reprocessed successfully'})
    except Exception as e:
        return jsonify({'error': f'Reprocessing failed: {str(e)}'}), 500

@app.route('/admin/storage-info', methods=['GET'])
def get_storage_info():
    """Get information about PDFs in storage folder"""
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            return jsonify({'pdfs': [], 'count': 0})
        
        pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.pdf')]
        pdf_info = []
        
        for filename in pdf_files:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file_size = os.path.getsize(filepath)
            pdf_info.append({
                'filename': filename,
                'size': file_size,
                'path': filepath
            })
        
        return jsonify({
            'pdfs': pdf_info,
            'count': len(pdf_files),
            'storage_path': UPLOAD_FOLDER
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get storage info: {str(e)}'}), 500

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
