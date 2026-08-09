"""
Text Cleaner
Clean and normalize extracted text
"""

import re
from typing import List

def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove multiple newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove common website artifacts
    text = re.sub(r'Cookie Policy|Accept Cookies|Subscribe to Newsletter', '', text, flags=re.IGNORECASE)
    
    return text

def remove_boilerplate(text: str) -> str:
    """
    Remove common boilerplate text
    """
    # Common patterns to remove
    patterns = [
        r'Skip to (main )?content',
        r'©.*?All rights reserved',
        r'Privacy Policy',
        r'Terms of Service',
        r'Cookie Policy',
        r'Follow us on.*',
        r'Subscribe to our newsletter',
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    
    # Remove spaces at start/end of lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()

def extract_sentences(text: str) -> list:
    """
    Split text into sentences
    
    Returns:
        List of sentences
    """
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    
    # Clean and filter
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences

def remove_urls(text: str) -> str:
    """Remove URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_pattern, '', text)

def remove_emails(text: str) -> str:
    """Remove email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.sub(email_pattern, '', text)

def clean_for_embedding(text: str) -> str:
    """
    Clean text specifically for embedding generation
    
    This removes noise that doesn't help semantic similarity
    """
    # Apply all cleaning steps
    text = clean_text(text)
    text = remove_boilerplate(text)
    text = normalize_whitespace(text)
    
    # Remove very short texts (likely noise)
    if len(text) < 20:
        return ""
    
    return text
