"""
Retriever
Retrieve relevant chunks using similarity search
"""

from typing import List, Dict
import chromadb
from rag.embeddings import generate_embedding
from rag.vectordb import query_vector_db



def retrieve_relevant_chunks(
    query: str,
    collection: chromadb.Collection,
    top_k: int = 8
) -> List[Dict]:

    query_embedding = generate_embedding(query)
    
    results = query_vector_db(
        collection=collection,
        query_embedding=query_embedding.tolist(),
        top_k=top_k
    )
    print("Requested top_k =", top_k)

    if results["documents"]:
        print(
            "Returned chunks =",
            len(results["documents"][0])
        )
    
    chunks = []
    
    if results['documents'] and len(results['documents']) > 0:
        for i in range(len(results['documents'][0])):
            chunk = {
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else 0,
                'id': results['ids'][0][i] if results['ids'] else ''
            }
            chunks.append(chunk)
    
    return chunks

def retrieve_with_filter(
    query: str,
    collection: chromadb.Collection,
    metadata_filter: Dict,
    top_k: int = 8
) -> List[Dict]:

    query_embedding = generate_embedding(query)
    
    results = query_vector_db(
        collection=collection,
        query_embedding=query_embedding.tolist(),
        top_k=top_k,
        filter_metadata=metadata_filter
    )
    

    chunks = []
    
    if results['documents'] and len(results['documents']) > 0:
        for i in range(len(results['documents'][0])):
            chunk = {
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else 0,
                'id': results['ids'][0][i] if results['ids'] else ''
            }
            chunks.append(chunk)
    
    return chunks

def rerank_chunks(chunks: List[Dict], query: str) -> List[Dict]:
    
    
    return chunks

def deduplicate_chunks(chunks: List[Dict], similarity_threshold: float = 0.95) -> List[Dict]:
    
    if not chunks:
        return []
    
    unique_chunks = [chunks[0]]
    
    for chunk in chunks[1:]:
        is_duplicate = False
        
        for unique_chunk in unique_chunks:
            if chunk['text'] == unique_chunk['text']:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_chunks.append(chunk)
    
    return unique_chunks
