"""
Text chunking service with token-aware splitting
Handles intelligent text segmentation for RAG processing
"""

import tiktoken
from typing import List, Dict, Any
import re

class TextChunker:
    """Handles token-aware text chunking for RAG processing"""
    
    def __init__(self, 
                 chunk_size: int = 400, 
                 chunk_overlap: int = 80,
                 model_name: str = "cl100k_base"):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Target number of tokens per chunk
            chunk_overlap: Number of tokens to overlap between chunks
            model_name: Tiktoken model name for tokenization
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(model_name)
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into sentences for better chunking
        
        Args:
            text: Input text to split
            
        Returns:
            List of sentences
        """
        # Split by sentences, keeping delimiters
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def chunk_text(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """
        Chunk text into overlapping segments
        
        Args:
            text: Input text to chunk
            filename: Source filename for metadata
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not text.strip():
            return []
        
        # Clean and normalize text
        text = self.clean_text(text)
        
        # Split into sentences
        sentences = self.split_text(text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, finalize current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Create chunk from current sentences
                chunk_text = ' '.join(current_chunk)
                chunks.append(self.create_chunk_metadata(
                    chunk_text, filename, chunk_id, current_tokens
                ))
                
                # Start new chunk with overlap
                current_chunk, current_tokens = self.create_overlap_chunk(
                    current_chunk, chunk_text
                )
                chunk_id += 1
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add final chunk if it has content
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(self.create_chunk_metadata(
                chunk_text, filename, chunk_id, current_tokens
            ))
        
        return chunks
    
    def create_chunk_metadata(self, chunk_text: str, filename: str, 
                            chunk_id: int, token_count: int) -> Dict[str, Any]:
        """
        Create metadata for a text chunk
        
        Args:
            chunk_text: The chunk text content
            filename: Source filename
            chunk_id: Unique chunk identifier
            token_count: Number of tokens in chunk
            
        Returns:
            Chunk metadata dictionary
        """
        return {
            'id': f"{filename}_{chunk_id}",
            'text': chunk_text,
            'filename': filename,
            'chunk_id': chunk_id,
            'token_count': token_count,
            'metadata': {
                'source': filename,
                'chunk_id': chunk_id,
                'token_count': token_count
            }
        }
    
    def create_overlap_chunk(self, previous_chunk: List[str], 
                           previous_text: str) -> tuple[List[str], int]:
        """
        Create overlap for next chunk based on previous chunk
        
        Args:
            previous_chunk: Previous chunk sentences
            previous_text: Previous chunk text
            
        Returns:
            Tuple of (overlap_sentences, overlap_tokens)
        """
        if not previous_chunk:
            return [], 0
        
        # Calculate how many tokens we want for overlap
        target_overlap_tokens = min(self.chunk_overlap, self.chunk_size // 2)
        
        # Start from the end and work backwards
        overlap_sentences = []
        overlap_tokens = 0
        
        for sentence in reversed(previous_chunk):
            sentence_tokens = self.count_tokens(sentence)
            if overlap_tokens + sentence_tokens <= target_overlap_tokens:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break
        
        return overlap_sentences, overlap_tokens
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def chunk_with_metadata(self, text: str, filename: str, 
                          page_numbers: List[int] = None) -> List[Dict[str, Any]]:
        """
        Chunk text with additional metadata like page numbers
        
        Args:
            text: Input text to chunk
            filename: Source filename
            page_numbers: List of page numbers for each chunk
            
        Returns:
            List of chunk dictionaries with enhanced metadata
        """
        chunks = self.chunk_text(text, filename)
        
        # Add page number information if available
        if page_numbers and len(page_numbers) == len(chunks):
            for i, chunk in enumerate(chunks):
                chunk['metadata']['page_number'] = page_numbers[i]
        
        return chunks
