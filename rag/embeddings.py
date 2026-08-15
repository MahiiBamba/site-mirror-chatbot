
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    
    if _embedding_model is None:
        print("Loading embedding model...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded!")
    
    return _embedding_model

def generate_embedding(text: str) -> np.ndarray:
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding

def generate_embeddings(chunks: List[Dict]) -> List[Dict]:
    model = get_embedding_model()
    
    texts = [chunk['text'] for chunk in chunks]
    
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
        batch_size=32
    )
    
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i]
    
    print("Embeddings generated!")
    
    return chunks

def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    similarity = dot_product / (norm1 * norm2)
    
    return float(similarity)

def get_embedding_dimension() -> int:
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()
