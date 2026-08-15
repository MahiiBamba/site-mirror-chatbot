
import re
from typing import List, Dict

def extract_faqs(crawl_data: Dict) -> List[Dict]:
   
    pages = crawl_data.get('pages', [])
    faqs = []
    
    for page in pages:
        page_faqs = extract_faqs_from_page(page)
        faqs.extend(page_faqs)
    
  
    seen_questions = set()
    unique_faqs = []
    
    for faq in faqs:
        q_lower = faq['question'].lower()
        if q_lower not in seen_questions:
            seen_questions.add(q_lower)
            unique_faqs.append(faq)
    
    return unique_faqs[:20]  

def extract_faqs_from_page(page: Dict) -> List[Dict]:
   
    faqs = []
    structured = page.get('structured', {})
    headings = structured.get('headings', [])
    paragraphs = structured.get('paragraphs', [])
    
    
    for i, heading in enumerate(headings):
        heading_text = heading.get('text', '').strip()
        
        
        if is_question(heading_text):
           
            answer = find_answer_after_heading(i, headings, paragraphs)
            
            if answer:
                faqs.append({
                    'question': heading_text,
                    'answer': answer,
                    'source': page.get('url', 'Unknown')
                })
    
    text = page.get('text', '')
    pattern_faqs = extract_qa_patterns(text, page.get('url', 'Unknown'))
    faqs.extend(pattern_faqs)
    
    return faqs

def is_question(text: str) -> bool:
    
    if '?' in text:
        return True
    
    question_words = [
        'what', 'when', 'where', 'who', 'why', 'how',
        'can', 'could', 'would', 'should', 'is', 'are',
        'does', 'do', 'did', 'will'
    ]
    
    text_lower = text.lower()
    
    for word in question_words:
        if text_lower.startswith(word + ' '):
            return True
    
    return False

def find_answer_after_heading(
    heading_idx: int,
    headings: List[Dict],
    paragraphs: List[str]
) -> str:
   
    if heading_idx < len(paragraphs):
        
        answer = paragraphs[heading_idx] if heading_idx < len(paragraphs) else ""
        
       
        if answer and len(answer) > 20 and len(answer) < 500:
            return answer
    
    return ""

def extract_qa_patterns(text: str, source_url: str) -> List[Dict]:
    
    faqs = []
    
    pattern = r'Q[:\.]?\s*(.+?)\s*A[:\.]?\s*(.+?)(?=Q[:\.]|$)'
    matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        question = match.group(1).strip()
        answer = match.group(2).strip()
        
        
        question = re.sub(r'\s+', ' ', question)
        answer = re.sub(r'\s+', ' ', answer)
        
        if len(question) > 10 and len(question) < 200 and len(answer) > 10 and len(answer) < 500:
            faqs.append({
                'question': question,
                'answer': answer,
                'source': source_url
            })
    
    return faqs
