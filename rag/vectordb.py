
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import os
from pathlib import Path


_chroma_client = None
_current_collection = None

def get_chroma_client():
   
    global _chroma_client
    
    if _chroma_client is None:
        
        db_path = Path("data/chromadb")
        db_path.mkdir(parents=True, exist_ok=True)
        
        _chroma_client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    
    return _chroma_client

import re

def sanitize_collection_name(name: str) -> str:
    
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    
    name = name.rstrip("_-")
   
    if len(name) < 3:
        name = f"{name}123"
    if len(name) > 63:
        name = name[:63].rstrip("_-")
    return name


def initialize_vector_db(collection_name: str = "site_mirror") -> chromadb.Collection:
    
    client = get_chroma_client()
    
    try:
        client.delete_collection(name=collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  
    )
    
    return collection

def store_embeddings(chunks_with_embeddings: List[Dict], source_url: str) -> chromadb.Collection:

    raw_name = "site_mirror_" + source_url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
   
    collection_name = sanitize_collection_name(raw_name)
    
    collection = initialize_vector_db(collection_name)
    
    ids = []
    embeddings = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks_with_embeddings):
        ids.append(f"chunk_{i}")
        embeddings.append(chunk['embedding'].tolist())
        documents.append(chunk['text'])
        metadatas.append(chunk.get('metadata', {}))
    
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        batch_end = min(i + batch_size, len(ids))
        
        collection.add(
            ids=ids[i:batch_end],
            embeddings=embeddings[i:batch_end],
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end]
        )
    
    print(f"Stored {len(ids)} embeddings in ChromaDB collection: {collection_name}")
    
    return collection

def query_vector_db(
    collection: chromadb.Collection,
    query_embedding: List[float],
    top_k: int = 8,
    filter_metadata: Optional[Dict] = None
) -> Dict:
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=filter_metadata
    )
    
    return results

def get_collection_stats(collection: chromadb.Collection) -> Dict:

    count = collection.count()
    
    return {
        'total_chunks': count,
        'name': collection.name
    }

def delete_collection(collection_name: str):
    
    client = get_chroma_client()
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted collection: {collection_name}")
    except Exception as e:
        print(f"Error deleting collection: {e}")
