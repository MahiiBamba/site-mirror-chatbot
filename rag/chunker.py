"""
Text Chunker
Split documents into chunks for embedding
"""

from typing import List, Dict
from scraper.cleaner import clean_for_embedding

class TextChunker:
    def __init__(self, chunk_size: int = 800, overlap: int = 150):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
        
        Returns:
            List of chunk dictionaries
        """
        if not text or len(text) < 20:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find end of chunk
            end = start + self.chunk_size
            
            # If not at end of text, try to break at sentence boundary
            if end < len(text):
                # Look for period, question mark, or exclamation
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_data = {
                    'text': chunk_text,
                    'start': start,
                    'end': end,
                    'metadata': metadata or {}
                }
                chunks.append(chunk_data)
            
            # Move start forward (with overlap)
            start = end - self.overlap if end < len(text) else len(text)
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text by paragraphs, combining small ones
        
        Args:
            text: Text to chunk
            metadata: Optional metadata
        
        Returns:
            List of chunk dictionaries
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': metadata or {}
                })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': metadata or {}
            })
        
        return chunks

def chunk_documents(pages: List[Dict], chunk_size: int = 800, overlap: int = 150) -> List[Dict]:
    """
    Chunk all documents from crawled pages
    
    Args:
        pages: List of page dictionaries from crawler
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
    
    Returns:
        List of all chunks with metadata
    """
    chunker = TextChunker(chunk_size, overlap)
    all_chunks = []
    
    for page in pages:
        # Clean text first
        text = clean_for_embedding(page.get('text', ''))
        
        if not text:
            continue
        
        # Create metadata for this page
        metadata = {
            'source_url': page.get('url', ''),
            'title': page.get('title', ''),
            'depth': page.get('depth', 0)
        }
        
        # Chunk the page
        chunks = chunker.chunk_text(text, metadata)
        all_chunks.extend(chunks)
    
    print(f"Created {len(all_chunks)} chunks from {len(pages)} pages")
    
    return all_chunks
