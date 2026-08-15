
from bs4 import BeautifulSoup
from typing import Dict, List
import re

def parse_html(html_content: str) -> BeautifulSoup:
    
    return BeautifulSoup(html_content, 'html.parser')

def extract_main_content(soup: BeautifulSoup) -> str:
    
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
        element.decompose()
    
    # Try to find main content area
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main'))
    
    if main_content:
        return main_content.get_text(separator='\n', strip=True)
    else:
        return soup.get_text(separator='\n', strip=True)

def extract_metadata(soup: BeautifulSoup) -> Dict:
    metadata = {
        'title': '',
        'description': '',
        'keywords': [],
        'author': ''
    }
    
    # Title
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.get_text().strip()
    
    # Meta description
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag and desc_tag.get('content'):
        metadata['description'] = desc_tag['content']
    
    # Meta keywords
    keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    if keywords_tag and keywords_tag.get('content'):
        metadata['keywords'] = [k.strip() for k in keywords_tag['content'].split(',')]
    
    # Author
    author_tag = soup.find('meta', attrs={'name': 'author'})
    if author_tag and author_tag.get('content'):
        metadata['author'] = author_tag['content']
    
    return metadata

def extract_links(soup: BeautifulSoup, base_url: str) -> List[Dict]:

    links = []
    
    for link in soup.find_all('a', href=True):
        link_data = {
            'url': link['href'],
            'text': link.get_text().strip(),
            'title': link.get('title', '')
        }
        links.append(link_data)
    
    return links

def extract_headings_hierarchy(soup: BeautifulSoup) -> List[Dict]:
    
    headings = []
    
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        headings.append({
            'level': int(heading.name[1]),
            'text': heading.get_text().strip()
        })
    
    return headings

def extract_tables(soup: BeautifulSoup) -> List[Dict]:
    
    tables = []
    
    for table in soup.find_all('table'):
        table_data = {
            'headers': [],
            'rows': []
        }
        
        # Extract headers
        headers = table.find_all('th')
        if headers:
            table_data['headers'] = [h.get_text().strip() for h in headers]
        
        # Extract rows
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if cells:
                row_data = [cell.get_text().strip() for cell in cells]
                table_data['rows'].append(row_data)
        
        if table_data['rows']:
            tables.append(table_data)
    
    return tables
