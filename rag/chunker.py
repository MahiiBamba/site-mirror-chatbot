

from typing import List, Dict
from scraper.cleaner import clean_for_embedding

class TextChunker:
    def __init__(self, chunk_size: int = 800, overlap: int = 150):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        if not text or len(text) < 20:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            if end < len(text):
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
            
            start = end - self.overlap if end < len(text) else len(text)
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str, metadata: Dict = None) -> List[Dict]:
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': metadata or {}
                })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': metadata or {}
            })
        
        return chunks

def chunk_documents(pages: List[Dict], chunk_size: int = 800, overlap: int = 150) -> List[Dict]:
    chunker = TextChunker(chunk_size, overlap)
    all_chunks = []
    
    for page in pages:
        text = clean_for_embedding(page.get('text', ''))
        
        if not text:
            continue
        
        metadata = {
            'source_url': page.get('url', ''),
            'title': page.get('title', ''),
            'depth': page.get('depth', 0)
        }
        
        chunks = chunker.chunk_text(text, metadata)
        all_chunks.extend(chunks)
    
    print(f"Created {len(all_chunks)} chunks from {len(pages)} pages")
    
    return all_chunks
