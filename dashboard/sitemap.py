"""
Sitemap Display
Visual representation of crawled site structure
"""

import streamlit as st
from typing import Dict, List
from urllib.parse import urlparse
from collections import defaultdict

def build_sitemap_tree(crawl_data: Dict) -> Dict:
    """
    Build a tree structure from crawled pages
    
    Args:
        crawl_data: Crawled website data
    
    Returns:
        Tree structure
    """
    pages = crawl_data.get('pages', [])
    base_url = crawl_data.get('base_url', '')
    
    # Parse base URL
    parsed_base = urlparse(base_url)
    base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
    
    # Group pages by depth
    tree = defaultdict(list)
    
    for page in pages:
        depth = page.get('depth', 0)
        url = page.get('url', '')
        title = page.get('title', url)
        
        # Get path from URL
        path = url.replace(base_domain, '')
        if not path:
            path = '/'
        
        tree[depth].append({
            'url': url,
            'title': title,
            'path': path
        })
    
    return dict(tree)

def display_sitemap(crawl_data: Dict):
    """
    Display sitemap in sidebar
    
    Args:
        crawl_data: Crawled website data
    """
    tree = build_sitemap_tree(crawl_data)
    
    if not tree:
        st.text("No pages to display")
        return
    
    # Display by depth
    for depth in sorted(tree.keys()):
        pages = tree[depth]
        
        for page in pages:
            # Indent based on depth
            indent = "  " * depth
            icon = "📄" if depth > 0 else "🏠"
            
            # Truncate long titles
            title = page['title']
            if len(title) > 30:
                title = title[:27] + "..."
            
            # Create clickable link
            st.markdown(
                f"{indent}{icon} [{title}]({page['url']})",
                unsafe_allow_html=True
            )

def create_sitemap_visualization(crawl_data: Dict) -> str:
    """
    Create ASCII-art style sitemap visualization
    
    Args:
        crawl_data: Crawled website data
    
    Returns:
        ASCII art sitemap
    """
    tree = build_sitemap_tree(crawl_data)
    
    lines = []
    lines.append("Site Structure:")
    lines.append("")
    
    for depth in sorted(tree.keys()):
        pages = tree[depth]
        
        for i, page in enumerate(pages):
            # Create tree characters
            if depth == 0:
                prefix = "🏠 "
            else:
                is_last = i == len(pages) - 1
                prefix = "  " * (depth - 1)
                prefix += "└── " if is_last else "├── "
            
            title = page['title']
            if len(title) > 40:
                title = title[:37] + "..."
            
            lines.append(f"{prefix}{title}")
    
    return "\n".join(lines)
