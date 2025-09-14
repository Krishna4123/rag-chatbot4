"""
Vector store service using Pinecone
Handles vector storage, retrieval, and management
"""

import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pinecone import Pinecone, ServerlessSpec
import time

class VectorStore:
    """Handles vector operations with Pinecone"""
    
    def __init__(self):
        """Initialize Pinecone vector store"""
        self.api_key = os.getenv('PINECONE_API_KEY')
        self.index_name = os.getenv('PINECONE_INDEX', 'career-rag-index')
        self.pc = None
        self.index = None
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        
        self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and index"""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists, create if not
            if self.index_name not in self.pc.list_indexes().names():
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                
                # Wait for index to be ready
                while not self.pc.describe_index(self.index_name).status['ready']:
                    print("Waiting for index to be ready...")
                    time.sleep(1)
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            print(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            raise

    def get_processed_filenames_in_namespace(self, namespace: str = "default") -> set[str]:
        """
        Retrieves a set of filenames that have already been processed and stored in the given namespace.
        This is done by querying Pinecone for all unique 'filename' metadata values.
        """
        try:
            # Fetch all unique filenames in the namespace
            # Pinecone's describe_index_stats includes namespace stats with filter info
            # However, direct fetching of all unique metadata values in a performant way
            # requires a bit of a workaround or specific client methods not directly exposed
            # to simplify, we'll perform a dummy query to get existing metadata if needed

            # A more robust solution might involve storing this list separately
            # or using Pinecone's list_objects with filter for production

            # For now, we'll try to get metadata from existing vectors
            # This can be slow for very large namespaces without specific metadata indexing
            # but works for smaller to medium scale. For production, consider client.list_vectors
            # or a separate database to track processed files.
            
            # For a simple check, we can list the first few vectors and extract filenames
            # or iterate if necessary. A more direct method is desirable.

            # As a pragmatic approach for avoiding re-ingestion, we'll use a cached list
            # or assume a file is processed if its name exists in the index after a query
            # For a truly accurate list, you might need to query the index.

            # Let's use a small query to check for existing filenames if the index is not empty
            stats = self.index.describe_index_stats()
            namespace_stats = stats.namespaces.get(namespace)

            if namespace_stats and namespace_stats.vector_count > 0:
                # Query with a dummy vector and filter to get some metadata, then extract filenames
                # This is a heuristic, not a comprehensive list for huge indices
                response = self.index.query(
                    vector=[0.0]*384, # Dummy vector for metadata-only retrieval
                    top_k=1000, # Retrieve a reasonable number of vectors
                    namespace=namespace,
                    include_metadata=True,
                    filter={'filename': {'$ne': ''}} # Filter for entries that have a filename
                )
                filenames = {match.metadata['filename'] for match in response.matches if 'filename' in match.metadata}
                return filenames
            return set()

        except Exception as e:
            print(f"Error getting processed filenames in namespace {namespace}: {e}")
            return set()
    
    def store_vectors(self, chunks: List[Dict[str, Any]], 
                     embeddings: List[List[float]], 
                     namespace: str = "default") -> bool:
        """
        Store text chunks and their embeddings in Pinecone
        
        Args:
            chunks: List of chunk dictionaries with metadata
            embeddings: List of embedding vectors
            namespace: Pinecone namespace for organization
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not chunks or not embeddings:
                print("No chunks or embeddings to store")
                return False
            
            if len(chunks) != len(embeddings):
                print(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")
                return False
            
            # Prepare vectors for Pinecone
            vectors_to_upsert = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{chunk['id']}_{uuid.uuid4().hex[:8]}"
                
                vector_data = {
                    'id': vector_id,
                    'values': embedding,
                    'metadata': {
                        'text': chunk['text'],
                        'filename': chunk['filename'],
                        'chunk_id': chunk['chunk_id'],
                        'token_count': chunk['token_count'],
                        **chunk.get('metadata', {})
                    }
                }
                vectors_to_upsert.append(vector_data)
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)
                print(f"Upserted batch {i//batch_size + 1}/{(len(vectors_to_upsert) + batch_size - 1)//batch_size}")
            
            print(f"Successfully stored {len(vectors_to_upsert)} vectors in namespace '{namespace}'")
            return True
            
        except Exception as e:
            print(f"Error storing vectors: {e}")
            return False
    
    def search_similar(self, query_embedding: List[float], 
                      top_k: int = 8, 
                      namespace: str = "default",
                      filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using query embedding
        
        Args:
            query_embedding: Query vector to search with
            top_k: Number of similar vectors to return
            namespace: Pinecone namespace to search in
            filter_dict: Optional metadata filter
            
        Returns:
            List of similar vectors with metadata
        """
        try:
            search_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
                filter=filter_dict
            )
            
            results = []
            for match in search_response.matches:
                result = {
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', ''),
                    'filename': match.metadata.get('filename', ''),
                    'chunk_id': match.metadata.get('chunk_id', 0),
                    'metadata': match.metadata
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []
    
    def get_vector_count(self, namespace: str = "default") -> int:
        """
        Get total number of vectors in namespace
        
        Args:
            namespace: Pinecone namespace
            
        Returns:
            Number of vectors
        """
        try:
            stats = self.index.describe_index_stats()
            return stats.namespaces.get(namespace, {}).get('vector_count', 0)
        except Exception as e:
            print(f"Error getting vector count: {e}")
            return 0
    
    def clear_namespace(self, namespace: str = "default") -> bool:
        """
        Clear all vectors from a namespace
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            print(f"Cleared all vectors from namespace '{namespace}'")
            return True
        except Exception as e:
            print(f"Error clearing namespace: {e}")
            return False
    
    def delete_vectors(self, vector_ids: List[str], namespace: str = "default") -> bool:
        """
        Delete specific vectors by ID
        
        Args:
            vector_ids: List of vector IDs to delete
            namespace: Namespace containing the vectors
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.index.delete(ids=vector_ids, namespace=namespace)
            print(f"Deleted {len(vector_ids)} vectors from namespace '{namespace}'")
            return True
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vector_count': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': {ns: {'vector_count': ns_stats.vector_count} 
                              for ns, ns_stats in stats.namespaces.items()}
            }
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}
    
    def search_by_metadata(self, filter_dict: Dict[str, Any], 
                          top_k: int = 10, 
                          namespace: str = "default") -> List[Dict[str, Any]]:
        """
        Search vectors by metadata filter
        
        Args:
            filter_dict: Metadata filter conditions
            top_k: Number of results to return
            namespace: Namespace to search in
            
        Returns:
            List of matching vectors
        """
        try:
            # Use a dummy vector for metadata-only search
            dummy_vector = [0.0] * 384
            
            search_response = self.index.query(
                vector=dummy_vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
                filter=filter_dict
            )
            
            results = []
            for match in search_response.matches:
                result = {
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', ''),
                    'filename': match.metadata.get('filename', ''),
                    'chunk_id': match.metadata.get('chunk_id', 0),
                    'metadata': match.metadata
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching by metadata: {e}")
            return []
