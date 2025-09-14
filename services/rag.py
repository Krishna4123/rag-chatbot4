"""
RAG (Retrieval-Augmented Generation) orchestration service for Medical Chatbot
Handles query processing, retrieval, and medical response generation
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore

class RAGService:
    """Orchestrates RAG pipeline for medical guidance chatbot"""
    
    def __init__(self):
        """Initialize RAG service with dependencies"""
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', 'openrouter/auto')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.openrouter_api_key:
            print("Warning: OPENROUTER_API_KEY not found. LLM responses will be disabled.")
    
    def query(self, user_query: str, persona: str = "doctor", 
              namespace: str = "default") -> Dict[str, Any]:
        """
        Process user query through RAG pipeline with OpenRouter fallback
        
        Args:
            user_query: User's medical question
            persona: AI persona (doctor/specialist/nurse)
            namespace: Vector store namespace
            
        Returns:
            Response dictionary with answer and sources
        """
        try:
            # Step 1: Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(user_query)
            
            # Step 2: Retrieve relevant chunks
            retrieved_chunks = self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=8,
                namespace=namespace
            )
            
            # Step 3: Check if we have sufficient relevant data
            has_sufficient_data = self._check_data_sufficiency(retrieved_chunks)
            
            if not has_sufficient_data:
                # Use OpenRouter's knowledge base as fallback
                return self._generate_openrouter_fallback(user_query, persona, retrieved_chunks)
            
            # Step 4: Build context with citations
            context, sources = self._build_context_with_citations(retrieved_chunks)
            
            # Step 5: Generate response using LLM with context
            if self.openrouter_api_key:
                response_text = self._generate_llm_response(
                    user_query, context, persona, sources
                )
            else:
                response_text = self._create_simple_response(context, sources)
            
            return {
                'answer': response_text,
                'sources': sources,
                'retrieved_chunks': len(retrieved_chunks),
                'persona': persona,
                'query': user_query,
                'data_source': 'pdf_documents'
            }
            
        except Exception as e:
            print(f"Error in RAG query: {e}")
            return {
                'answer': f"I apologize, but I encountered an error processing your question: {str(e)}",
                'sources': [],
                'retrieved_chunks': 0,
                'persona': persona,
                'query': user_query,
                'error': str(e)
            }
    
    def _check_data_sufficiency(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Check if retrieved chunks provide sufficient relevant data
        
        Args:
            chunks: Retrieved text chunks
            
        Returns:
            True if sufficient data, False otherwise
        """
        if not chunks:
            return False
        
        # Check if we have at least 3 chunks with reasonable relevance scores
        high_relevance_chunks = [chunk for chunk in chunks if chunk.get('score', 0) > 0.3]
        
        if len(high_relevance_chunks) < 3:
            return False
        
        # Check if the total context length is substantial
        total_context_length = sum(len(chunk.get('text', '')) for chunk in chunks)
        
        if total_context_length < 500:  # Less than 500 characters
            return False
        
        return True
    
    def _generate_openrouter_fallback(self, query: str, persona: str, 
                                    retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate response using OpenRouter's knowledge base when PDF data is insufficient
        
        Args:
            query: User's question
            persona: AI persona
            retrieved_chunks: Any retrieved chunks (may be empty or low relevance)
            
        Returns:
            Response dictionary
        """
        if not self.openrouter_api_key:
            return self._create_fallback_response(query, persona)
        
        try:
            # Create persona-specific system prompt for general medical knowledge
            system_prompt = self._get_persona_prompt(persona) + """
            
            You are responding based on your general medical knowledge. The user's question may not be fully covered by their uploaded documents, so provide comprehensive medical information based on established medical knowledge and best practices. Always emphasize that this is for informational purposes only and that they should consult healthcare professionals for medical advice."""
            
            # Include any relevant context from retrieved chunks if available
            context_note = ""
            if retrieved_chunks:
                context_note = f"\n\nNote: Some information from uploaded documents may be relevant, but the response below is primarily based on general medical knowledge."
            
            user_prompt = f"""Please provide a comprehensive answer to this medical question: {query}

{context_note}

Please provide detailed, accurate medical information while emphasizing that this is for informational purposes only and that professional medical consultation is recommended."""
            
            # Make API request to OpenRouter
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "RAG Medical Chatbot"
            }
            
            payload = {
                "model": self.openrouter_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1200
            }
            
            response = requests.post(
                self.openrouter_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                
                return {
                    'answer': answer,
                    'sources': [],  # No specific sources since using general knowledge
                    'retrieved_chunks': len(retrieved_chunks),
                    'persona': persona,
                    'query': query,
                    'data_source': 'openrouter_knowledge_base',
                    'fallback_used': True
                }
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._create_fallback_response(query, persona)
                
        except Exception as e:
            print(f"Error in OpenRouter fallback: {e}")
            return self._create_fallback_response(query, persona)
    
    def _build_context_with_citations(self, chunks: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        """
        Build context string with source citations
        
        Args:
            chunks: Retrieved text chunks
            
        Returns:
            Tuple of (context_string, sources_list)
        """
        context_parts = []
        sources = []
        
        for i, chunk in enumerate(chunks, 1):
            # Extract source information
            filename = chunk.get('filename', 'Unknown')
            chunk_id = chunk.get('chunk_id', 0)
            text = chunk.get('text', '')
            score = chunk.get('score', 0.0)
            
            # Create citation reference
            citation = f"[{i}]"
            source_info = {
                'citation': citation,
                'filename': filename,
                'chunk_id': chunk_id,
                'relevance_score': round(score, 3),
                'text_preview': text[:200] + "..." if len(text) > 200 else text
            }
            sources.append(source_info)
            
            # Add to context with citation
            context_parts.append(f"{citation} {text}")
        
        context = "\n\n".join(context_parts)
        return context, sources
    
    def _generate_llm_response(self, query: str, context: str, 
                              persona: str, sources: List[Dict[str, Any]]) -> str:
        """
        Generate response using OpenRouter LLM
        
        Args:
            query: User's question
            context: Retrieved context with citations
            persona: AI persona
            sources: List of source information
            
        Returns:
            Generated response text
        """
        try:
            # Create persona-specific system prompt
            system_prompt = self._get_persona_prompt(persona)
            
            # Create user prompt with context
            user_prompt = f"""Based on the following career guidance information, please answer the user's question. Use the provided sources to support your answer and include relevant citations.

Context Information:
{context}

User Question: {query}

Please provide a helpful, accurate response based on the context above. Include relevant citations from the sources when appropriate."""

            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "RAG Career Chatbot"
            }
            
            payload = {
                "model": self.openrouter_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            # Make API request
            response = requests.post(
                self.openrouter_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._create_simple_response(context, sources)
                
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return self._create_simple_response(context, sources)
    
    def _get_persona_prompt(self, persona: str) -> str:
        """
        Get persona-specific system prompt
        
        Args:
            persona: Persona type (doctor/specialist/nurse)
            
        Returns:
            System prompt string
        """
        prompts = {
            "doctor": """You are a knowledgeable and caring medical doctor. Your role is to provide accurate, evidence-based medical information and guidance. Be professional, empathetic, and thorough in your explanations. Always emphasize that this is for informational purposes only and that patients should consult with their healthcare providers for medical advice. Use clear, understandable language and provide practical health guidance.""",
            
            "specialist": """You are a medical specialist with deep expertise in various medical fields. Your role is to provide detailed, technical medical information based on the latest research and clinical guidelines. Be precise, cite medical sources frequently, and focus on evidence-based recommendations. Use professional medical terminology while remaining accessible. Always remind users to consult healthcare professionals for medical decisions.""",
            
            "nurse": """You are a compassionate and experienced registered nurse. Your role is to provide practical, patient-centered health guidance and education. Be warm, supportive, and focus on patient care, symptom management, and health promotion. Use clear, simple language and provide actionable health advice. Always emphasize the importance of professional medical care when needed."""
        }
        
        return prompts.get(persona, prompts["doctor"])
    
    def _create_simple_response(self, context: str, sources: List[Dict[str, Any]]) -> str:
        """
        Create a simple response when LLM is not available
        
        Args:
            context: Retrieved context
            sources: Source information
            
        Returns:
            Simple response text
        """
        if not context:
            return "I don't have enough information to answer your medical question. Please upload some medical documents first."
        
        # Create a simple summary of the most relevant chunks
        top_sources = sources[:3]  # Top 3 most relevant sources
        
        response = "Based on the available information, here's what I found:\n\n"
        
        for source in top_sources:
            response += f"• {source['text_preview']} (Source: {source['filename']})\n\n"
        
        response += "For more detailed medical guidance, please ensure you have uploaded relevant medical documents."
        
        return response
    
    def _create_fallback_response(self, query: str, persona: str) -> Dict[str, Any]:
        """
        Create fallback response when no relevant chunks are found
        
        Args:
            query: User's question
            persona: AI persona
            
        Returns:
            Fallback response dictionary
        """
        fallback_messages = {
            "doctor": "I'd be happy to help with your medical question! However, I don't have enough relevant medical information in my knowledge base to provide a comprehensive answer. Could you upload some medical documents so I can give you more accurate guidance?",
            
            "specialist": "I understand you're looking for medical information. To provide you with the most accurate and evidence-based guidance, I need access to relevant medical documents. Please upload some medical PDFs so I can assist you better.",
            
            "nurse": "I don't have sufficient medical information in my knowledge base to provide a thorough answer to your health question. Please upload relevant medical documents to enable me to give you better health guidance."
        }
        
        return {
            'answer': fallback_messages.get(persona, fallback_messages["doctor"]),
            'sources': [],
            'retrieved_chunks': 0,
            'persona': persona,
            'query': query,
            'fallback': True
        }
    
    def get_available_personas(self) -> List[Dict[str, str]]:
        """
        Get list of available AI personas
        
        Returns:
            List of persona information
        """
        return [
            {
                'id': 'doctor',
                'name': 'Medical Doctor',
                'description': 'Knowledgeable and caring medical guidance with professional expertise'
            },
            {
                'id': 'specialist',
                'name': 'Medical Specialist',
                'description': 'Detailed, technical medical information based on latest research'
            },
            {
                'id': 'nurse',
                'name': 'Registered Nurse',
                'description': 'Compassionate, patient-centered health guidance and education'
            }
        ]
