"""
Embeddings Generator
Convert text chunks into vector embeddings
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

# Global model instance (loaded once)
_embedding_model = None

def get_embedding_model():
    """Get or initialize the embedding model"""
    global _embedding_model
    
    if _embedding_model is None:
        print("Loading embedding model...")
        # Using a small, fast, and effective model
        # all-MiniLM-L6-v2: 384 dimensions, 80MB, good balance of speed/quality
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded!")
    
    return _embedding_model

def generate_embedding(text: str) -> np.ndarray:
    """
    Generate embedding for a single text
    
    Args:
        text: Text to embed
    
    Returns:
        Numpy array of embeddings
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding

def generate_embeddings(chunks: List[Dict]) -> List[Dict]:
    """
    Generate embeddings for all chunks
    
    Args:
        chunks: List of chunk dictionaries
    
    Returns:
        List of chunks with embeddings added
    """
    model = get_embedding_model()
    
    # Extract texts
    texts = [chunk['text'] for chunk in chunks]
    
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    # Generate embeddings in batch (faster)
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
        batch_size=32
    )
    
    # Add embeddings to chunks
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i]
    
    print("Embeddings generated!")
    
    return chunks

def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Similarity score (0-1)
    """
    # Cosine similarity
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    similarity = dot_product / (norm1 * norm2)
    
    return float(similarity)

def get_embedding_dimension() -> int:
    """Get the dimension of embeddings from current model"""
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()
