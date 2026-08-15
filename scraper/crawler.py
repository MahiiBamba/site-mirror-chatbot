
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Set
import re

class WebsiteCrawler:
    def __init__(self, base_url: str, max_depth: int = 1, max_pages: int = 1):
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.pages_data: List[Dict] = []
        self.all_links: Set[str] = set()
        
        # Parse base domain
        parsed = urlparse(base_url)
        self.base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
    def is_valid_url(self, url: str) -> bool:
       
        if not url or url in self.visited_urls:
            return False
        
        # Must be from same domain
        if not url.startswith(self.base_domain):
            return False
        
        # Skip common non-content URLs
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.zip', '.exe']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip anchors
        if '#' in url:
            url = url.split('#')[0]
        
        return True
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful text from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Remove blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_structured_content(self, soup: BeautifulSoup) -> Dict:
        
        content = {
            'title': '',
            'headings': [],
            'paragraphs': [],
            'lists': []
        }
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            content['title'] = title_tag.get_text().strip()
        
        # Headings (h1, h2, h3)
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            content['headings'].append({
                'level': heading.name,
                'text': heading.get_text().strip()
            })
        
        # Paragraphs
        for para in soup.find_all('p'):
            text = para.get_text().strip()
            if len(text) > 20:  # Only substantial paragraphs
                content['paragraphs'].append(text)
        
        # Lists
        for ul in soup.find_all(['ul', 'ol']):
            list_items = [li.get_text().strip() for li in ul.find_all('li')]
            if list_items:
                content['lists'].append(list_items)
        
        return content
    
    def crawl_page(self, url: str, depth: int) -> None:
        """Crawl a single page"""
        if len(self.pages_data) >= self.max_pages:
            return
        
        if not self.is_valid_url(url) or depth > self.max_depth:
            return
        
        try:
            print(f"Crawling: {url} (depth: {depth})")
            
            # Add headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            self.visited_urls.add(url)
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            text_content = self.extract_text_content(soup)
            structured_content = self.extract_structured_content(soup)
            
            # Store page data
            page_data = {
                'url': url,
                'title': structured_content['title'],
                'text': text_content,
                'structured': structured_content,
                'depth': depth
            }
            
            self.pages_data.append(page_data)
            
            # Find links for next level
            if depth < self.max_depth:
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    # Remove query parameters and fragments for cleaner URLs
                    next_url = next_url.split('?')[0].split('#')[0]
                    
                    self.all_links.add(next_url)
                    
                    if self.is_valid_url(next_url) and len(self.pages_data) < self.max_pages:
                        time.sleep(0.5)  # Be polite
                        self.crawl_page(next_url, depth + 1)
            
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
    
    def crawl(self) -> Dict:
        """Start crawling from base URL"""
        print(f"Starting crawl of {self.base_url}")
        self.crawl_page(self.base_url, 0)
        
        return {
            'base_url': self.base_url,
            'pages': self.pages_data,
            'all_links': list(self.all_links),
            'total_pages': len(self.pages_data)
        }

def crawl_website(url: str, max_depth: int = 1, max_pages: int = 1) -> Dict:

    crawler = WebsiteCrawler(url, max_depth, max_pages)
    return crawler.crawl()
