"""
Streamlit frontend for RAG Medical Chatbot
Provides user interface for PDF upload, chat, and medical guidance
"""

import streamlit as st
import requests
import os
from typing import List, Dict, Any
import time

# Page configuration
st.set_page_config(
    page_title="RAG Career Chatbot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

class MedicalChatbotUI:
    """Main UI class for the medical chatbot"""
    
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'selected_persona' not in st.session_state:
            st.session_state.selected_persona = 'doctor'
        if 'namespace' not in st.session_state:
            st.session_state.namespace = 'default'
    
    def check_backend_health(self) -> bool:
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.backend_url}/admin/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def upload_pdf(self, uploaded_file) -> Dict[str, Any]:
        """Upload PDF to backend for processing"""
        try:
            files = {'file': uploaded_file}
            response = requests.post(
                f"{self.backend_url}/ingest",
                files=files,
                timeout=60
            )
            return response.json()
        except Exception as e:
            return {'error': f'Upload failed: {str(e)}'}
    
    def send_chat_message(self, message: str, persona: str, namespace: str) -> Dict[str, Any]:
        """Send chat message to backend"""
        try:
            payload = {
                'query': message,
                'persona': persona,
                'namespace': namespace
            }
            response = requests.post(
                f"{self.backend_url}/chat",
                json=payload,
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {'error': f'Chat failed: {str(e)}'}
    
    def clear_namespace(self, namespace: str) -> Dict[str, Any]:
        """Clear vectors from namespace"""
        try:
            payload = {'namespace': namespace}
            response = requests.post(
                f"{self.backend_url}/admin/clear",
                json=payload,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'error': f'Clear failed: {str(e)}'}
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about PDFs in storage folder"""
        try:
            response = requests.get(f"{self.backend_url}/admin/storage-info", timeout=10)
            return response.json()
        except Exception as e:
            return {'error': f'Failed to get storage info: {str(e)}'}
    
    def reprocess_storage(self) -> Dict[str, Any]:
        """Reprocess all PDFs in storage folder"""
        try:
            response = requests.post(f"{self.backend_url}/admin/reprocess", timeout=60)
            return response.json()
        except Exception as e:
            return {'error': f'Reprocessing failed: {str(e)}'}

def main():
    """Main application function"""
    ui = MedicalChatbotUI()
    
    # Header
    st.title("🏥 RAG Medical Chatbot")
    st.markdown("Get personalized medical guidance powered by AI and your medical documents")
    
    # Check backend health
    if not ui.check_backend_health():
        st.error("⚠️ Backend server is not running. Please start the Flask server first.")
        st.code("python app.py")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Document Management")
        
        # PDF Upload
        uploaded_files = st.file_uploader(
            "Upload Medical Documents",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload PDF files containing medical information, research papers, or health guidelines"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in [f['name'] for f in st.session_state.uploaded_files]:
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        result = ui.upload_pdf(uploaded_file)
                        
                        if 'error' in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success(f"✅ {result['message']}")
                            st.session_state.uploaded_files.append({
                                'name': uploaded_file.name,
                                'chunks': result.get('chunks_created', 0)
                            })
        
        # Display storage information
        st.subheader("📋 Document Storage")
        
        # Get storage info
        storage_info = ui.get_storage_info()
        
        if 'error' in storage_info:
            st.error(f"❌ {storage_info['error']}")
        else:
            if storage_info.get('count', 0) > 0:
                st.success(f"✅ {storage_info['count']} PDFs found in storage")
                for pdf in storage_info.get('pdfs', []):
                    size_mb = pdf['size'] / (1024 * 1024)
                    st.write(f"• {pdf['filename']} ({size_mb:.1f} MB)")
            else:
                st.info("No PDFs found in storage folder")
                st.write("Place PDF files in the `storage/pdfs/` folder and they will be automatically processed.")
        
        # Reprocess button
        if st.button("🔄 Reprocess Storage PDFs", help="Reprocess all PDFs in the storage folder"):
            with st.spinner("Reprocessing PDFs..."):
                result = ui.reprocess_storage()
                if 'error' in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success("✅ PDFs reprocessed successfully")
                    st.rerun()
        
        st.divider()
        
        # Persona Selection
        st.header("🤖 AI Persona")
        persona_options = {
            'doctor': '👨‍⚕️ Medical Doctor - Knowledgeable and caring',
            'specialist': '🔬 Medical Specialist - Technical and research-based',
            'nurse': '👩‍⚕️ Registered Nurse - Compassionate and patient-centered'
        }
        
        selected_persona = st.selectbox(
            "Choose your AI assistant style:",
            options=list(persona_options.keys()),
            format_func=lambda x: persona_options[x],
            index=list(persona_options.keys()).index(st.session_state.selected_persona)
        )
        st.session_state.selected_persona = selected_persona
        
        st.divider()
        
        # Namespace Management
        st.header("🗂️ Data Management")
        namespace = st.text_input(
            "Namespace (for organizing documents):",
            value=st.session_state.namespace,
            help="Use different namespaces to organize different sets of documents"
        )
        st.session_state.namespace = namespace
        
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.session_state.namespace:
                with st.spinner("Clearing data..."):
                    result = ui.clear_namespace(st.session_state.namespace)
                    if 'error' in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.success("✅ Data cleared successfully")
                        st.session_state.uploaded_files = []
                        st.session_state.chat_history = []
                        st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Medical Chat")
        
        # Chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(message['content'])
                else:
                    with st.chat_message("assistant"):
                        st.write(message['content'])
                        
                        # Display sources if available
                        if 'sources' in message and message['sources']:
                            with st.expander("📚 Sources"):
                                for source in message['sources']:
                                    st.write(f"**{source['filename']}** (Relevance: {source['relevance_score']:.2f})")
                                    st.write(f"*{source['text_preview']}*")
                        
                        # Display data source information
                        if 'data_source' in message:
                            data_source = message['data_source']
                            if data_source == 'pdf_documents':
                                st.caption("📄 Answer based on uploaded documents")
                            elif data_source == 'openrouter_knowledge_base':
                                st.caption("🧠 Answer based on AI knowledge base")
                        
                        if message.get('fallback_used'):
                            st.info("ℹ️ Using AI knowledge base as fallback (insufficient document data)")
        
        # Chat input
        user_input = st.chat_input(
            f"Ask me anything about your health as a {st.session_state.selected_persona}...",
            key="chat_input"
        )
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': time.time()
            })
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = ui.send_chat_message(
                        user_input, 
                        st.session_state.selected_persona,
                        st.session_state.namespace
                    )
                
                if 'error' in response:
                    st.error(f"❌ {response['error']}")
                    ai_message = f"I apologize, but I encountered an error: {response['error']}"
                else:
                    ai_message = response.get('answer', 'I apologize, but I could not generate a response.')
                    
                    # Display sources if available
                    if 'sources' in response and response['sources']:
                        with st.expander("📚 Sources"):
                            for source in response['sources']:
                                st.write(f"**{source['filename']}** (Relevance: {source['relevance_score']:.2f})")
                                st.write(f"*{source['text_preview']}*")
                
                st.write(ai_message)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': ai_message,
                'sources': response.get('sources', []),
                'timestamp': time.time()
            })
    
    with col2:
        st.header("ℹ️ Info")
        
        # Statistics
        storage_info = ui.get_storage_info()
        if 'error' not in storage_info and storage_info.get('count', 0) > 0:
            st.metric("PDFs in Storage", storage_info['count'])
            total_size = sum(pdf['size'] for pdf in storage_info.get('pdfs', []))
            st.metric("Total Size", f"{total_size / (1024*1024):.1f} MB")
        else:
            st.info("No PDFs in storage")
        
        # Vector database info
        try:
            # This would need to be implemented as an API endpoint
            st.metric("Vector Chunks", "Check backend logs")
        except:
            st.metric("Vector Chunks", "Unknown")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        
        if st.button("💡 Sample Questions"):
            sample_questions = [
                "What are the symptoms of diabetes and how is it managed?",
                "How can I prevent heart disease through lifestyle changes?",
                "What are the treatment options for high blood pressure?",
                "How do I recognize the signs of a stroke?",
                "What are the benefits and risks of different medications?"
            ]
            
            for question in sample_questions:
                if st.button(question, key=f"sample_{question[:20]}"):
                    st.session_state.chat_input = question
                    st.rerun()
        
        # Clear chat history
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
        
        # Help section
        st.subheader("❓ Help")
        st.markdown("""
        **How to use:**
        1. Upload PDF documents about medical topics
        2. Choose your preferred AI persona
        3. Ask medical and health questions
        4. Get personalized medical guidance with sources
        
        **Important Disclaimer:**
        - This is for informational purposes only
        - Always consult healthcare professionals
        - Not a substitute for medical advice
        - Emergency situations require immediate medical attention
        """)

if __name__ == "__main__":
    main()
