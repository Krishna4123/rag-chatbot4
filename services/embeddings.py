"""
Embeddings service using Hugging Face sentence-transformers
Handles text embedding generation for vector storage
"""

import os
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np

class EmbeddingService:
    """Handles text embedding generation using Hugging Face models"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedding service
        
        Args:
            model_name: Hugging Face model name for embeddings
        """
        self.model_name = model_name or os.getenv('HF_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            # Fallback to default model
            try:
                self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                print("Loaded fallback model: all-MiniLM-L6-v2")
            except Exception as fallback_error:
                raise Exception(f"Failed to load any embedding model: {fallback_error}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        if not text.strip():
            return [0.0] * self.model.get_sentence_embedding_dimension()
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.model.get_sentence_embedding_dimension()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text.strip()]
        if not valid_texts:
            return [[0.0] * self.model.get_sentence_embedding_dimension()] * len(texts)
        
        try:
            embeddings = self.model.encode(valid_texts, convert_to_tensor=False)
            
            # Handle case where some texts were empty
            if len(valid_texts) != len(texts):
                result = []
                valid_idx = 0
                for text in texts:
                    if text.strip():
                        result.append(embeddings[valid_idx].tolist())
                        valid_idx += 1
                    else:
                        result.append([0.0] * self.model.get_sentence_embedding_dimension())
                return result
            else:
                return embeddings.tolist()
                
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.model.get_sentence_embedding_dimension()] * len(texts)
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model
        
        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_info(self) -> dict:
        """
        Get information about the current model
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.get_embedding_dimension(),
            'max_seq_length': getattr(self.model, 'max_seq_length', 'unknown')
        }
    
    def batch_encode(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings in batches for large datasets
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.generate_embeddings(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (-1 to 1)
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
