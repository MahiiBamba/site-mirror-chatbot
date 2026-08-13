"""
Site-Mirror Chatbot
AI-Powered Website Mirror Dashboard with RAG Chat
"""

import streamlit as st
import sys
from pathlib import Path
from database import create_conversation, save_message, get_conversation_history, format_conversation_history

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = create_conversation()

print("CONVERSATION ID:", st.session_state.conversation_id)

history_text = format_conversation_history(
    st.session_state.conversation_id
)

print("FORMATTED HISTORY:")
print(history_text)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard.summary import generate_site_summary
from dashboard.faq_extractor import extract_faqs
from dashboard.sitemap import display_sitemap
from scraper.crawler import crawl_website
from rag.vectordb import initialize_vector_db, store_embeddings
from rag.retriever import retrieve_relevant_chunks
from rag.qa_chain import generate_answer, rewrite_query
from rag.chunker import chunk_documents
from rag.embeddings import generate_embeddings
import json
import os

# Page config
st.set_page_config(
    page_title="Site-Mirror Chatbot",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Manrope:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #0A4D68;
        --secondary: #088395;
        --accent: #05BFDB;
        --bg-dark: #001524;
        --text-primary: #1a1a1a;
        --text-secondary: #4a4a4a;
        --border: #e0e0e0;
        --success: #2ecc71;
        --warning: #f39c12;
    }
    
    /* Typography */
    h1, h2, h3, h4 {
        font-family: 'Crimson Pro', serif !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
    }
    
    p, div, span, label {
        font-family: 'Manrope', sans-serif !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A4D68 0%, #001524 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: white !important;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background: var(--success);
        color: white;
    }
    
    .status-processing {
        background: var(--warning);
        color: white;
    }
    
    .status-idle {
        background: var(--border);
        color: var(--text-secondary);
    }
    
    /* Cards */
    .metric-card {
        background: black;
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        margin-top: 0;
        color: var(--primary) !important;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .user-message {
        background: #1a1a1a !important;
        border-left-color: var(--secondary);
    }
    
    .bot-message {
        background: #1a1a1a !important;
        border-left-color: var(--success);
    }
    
    .source-tag {
        display: inline-block;
        background: var(--accent);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--secondary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Manrope', sans-serif !important;
        transition: all 0.3s !important;
    }
    
    .stButton > button:hover {
        background: var(--primary) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.8rem !important;
        font-family: 'Manrope', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--secondary) !important;
        box-shadow: 0 0 0 2px rgba(8, 131, 149, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'crawl_data' not in st.session_state:
    st.session_state.crawl_data = None
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'crawl_status' not in st.session_state:
    st.session_state.crawl_status = 'idle'  # idle, processing, complete

# Sidebar
with st.sidebar:
    st.markdown("# 🔍 Site-Mirror")
    st.markdown("### AI-Powered Website Intelligence")
    
    st.markdown("---")
    
    # URL Input
    st.markdown("#### 🌐 Website URL")
    url = st.text_input(
        "Enter URL to mirror",
        placeholder="https://example.com",
        label_visibility="collapsed"
    )
    
    # Crawl settings
    st.markdown("#### ⚙️ Crawl Settings")
    max_depth = st.slider("Max Depth", 1, 3, 2)
    max_pages = st.slider("Max Pages", 1, 50, 20)
    
    # Crawl button
    if st.button("🚀 Start Crawling", use_container_width=True):
        if url:
            st.session_state.crawl_status = 'processing'
            with st.spinner("Crawling website..."):
                try:
                    # Crawl website
                    crawl_results = crawl_website(url, max_depth=max_depth, max_pages=max_pages)
                    st.session_state.crawl_data = crawl_results

                    # Reset old state
                    st.session_state.site_summary = None
                    st.session_state.faqs = None
                    st.session_state.chat_history = []

                    # Chunk documents
                    chunks = chunk_documents(crawl_results['pages'])

                    # Generate embeddings
                    embeddings_data = generate_embeddings(chunks)

                    # Store in vector DB
                    vector_db = store_embeddings(embeddings_data, url)
                    st.session_state.vector_db = vector_db

                    st.session_state.crawl_status = 'complete'
                    st.success("✅ Crawling complete!")
                    st.rerun()

                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.crawl_status = 'idle'
        else:
            st.warning("Please enter a URL")
    
    # Status indicator
    st.markdown("---")
    st.markdown("#### 📊 Status")
    if st.session_state.crawl_status == 'idle':
        st.markdown('<div class="status-badge status-idle">⚪ Ready</div>', unsafe_allow_html=True)
    elif st.session_state.crawl_status == 'processing':
        st.markdown('<div class="status-badge status-processing">🟡 Processing</div>', unsafe_allow_html=True)
    elif st.session_state.crawl_status == 'complete':
        st.markdown('<div class="status-badge status-success">🟢 Complete</div>', unsafe_allow_html=True)
    
    # Sitemap (if available)
    if st.session_state.crawl_data:
        st.markdown("---")
        st.markdown("#### 🗺️ Sitemap")
        display_sitemap(st.session_state.crawl_data)

# Main content
if st.session_state.crawl_status == 'idle':
    # Welcome screen
    st.markdown("# 🔍 Welcome to Site-Mirror Chatbot")
    st.markdown("### Transform any website into an intelligent knowledge base")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📚 Mirror Website</h3>
            <p>Crawl and index any public website in seconds</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>💬 Chat Interface</h3>
            <p>Ask questions and get instant answers</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Source Citations</h3>
            <p>Every answer linked to original sources</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    1. **Enter a URL** in the sidebar (e.g., `https://docs.anthropic.com`)
    2. **Configure crawl settings** (depth and max pages)
    3. **Click 'Start Crawling'** to begin indexing
    4. **Chat with the mirrored site** once processing is complete
    
    ---
    
    ### ✨ Key Features
    
    - **Intelligent Crawling**: Discovers and indexes site structure automatically
    - **FAQ Extraction**: Automatically detects questions and answers
    - **RAG-Powered Chat**: Retrieval-Augmented Generation for accurate responses
    - **Source Attribution**: Every answer includes page sources
    - **Mirror Mode**: Responses strictly from indexed content (no hallucinations)
    """)

elif st.session_state.crawl_status == 'complete' and st.session_state.crawl_data:
    # Dashboard view
    st.markdown("# 📊 Website Mirror Dashboard")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🏠 Overview", "❓ FAQs", "💬 Chat"])
    
    with tab1:
    # Site summary
        st.markdown("## 📝 Site Summary")
        if st.session_state.site_summary is None:
            with st.spinner("Generating AI summary..."):
                try:
                    st.session_state.site_summary = generate_site_summary(st.session_state.crawl_data)
                except Exception as e:
                    st.error(f"❌ Error generating summary: {e}")
                    st.session_state.site_summary = {
                        "title": "Website Overview",
                        "summary": "Summary could not be generated.",
                        "topics": []
                    }

        summary_data = st.session_state.site_summary or {
            "title": "Website Overview",
            "summary": "No summary available",
            "topics": []
        }

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌐 {summary_data.get('title')}</h3>
                <p style="font-size: 1.1rem; line-height: 1.6; color: var(--text-secondary);">
                    {summary_data.get('summary')}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Statistics</h3>
            """, unsafe_allow_html=True)

            st.metric("Pages Indexed", len(st.session_state.crawl_data['pages']))
            st.metric("Total Links", len(st.session_state.crawl_data['all_links']))

            st.markdown("</div>", unsafe_allow_html=True)

        # Topics
        if summary_data.get('topics'):
            st.markdown("### 🏷️ Detected Topics")
            topics_html = " ".join([f'<span class="source-tag">{topic}</span>' for topic in summary_data['topics']])
            st.markdown(topics_html, unsafe_allow_html=True)


    
    with tab2:
        # FAQs
        st.markdown("## ❓ Frequently Asked Questions")
        
        if 'faqs' not in st.session_state:
            with st.spinner("Extracting FAQs..."):
                st.session_state.faqs = extract_faqs(st.session_state.crawl_data)
        
        faqs = st.session_state.faqs
        
        if faqs:
            for i, faq in enumerate(faqs):
                with st.expander(f"**Q: {faq['question']}**"):
                    st.markdown(faq['answer'])
                    st.markdown(f"*Source: `{faq['source']}`*")
        else:
            st.info("No FAQs detected on this website")
    
    with tab3:
        # Chat interface
        st.markdown("## 💬 Chat with Website")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                sources_html = ""
                if message.get('sources'):
                    sources_html = "<br><strong>Sources:</strong> " + " ".join([
                        f'<span class="source-tag">{s}</span>' for s in message['sources']
                    ])
                
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>Assistant:</strong> {message['content']}
                    {sources_html}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        user_question = st.text_input(
            "Ask a question about the website",
            placeholder="e.g., What is the refund policy?",
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Send", use_container_width=True):
                if user_question:


                    history_text = format_conversation_history(
                        st.session_state.conversation_id
                    )

                    rewritten_question = rewrite_query(
                        user_question,
                        history_text
                    )

                    print("ORIGINAL QUESTION:", user_question)
                    print("REWRITTEN QUESTION:", rewritten_question)

                    # Save user message to database
                    save_message(
                        st.session_state.conversation_id,
                        "user",
                        user_question
                    )

                    # Add user message to Streamlit chat history
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': user_question
                    })

                    with st.spinner("Thinking..."):
                        # Retrieve relevant chunks
                        relevant_chunks = retrieve_relevant_chunks(
                            user_question,
                            st.session_state.vector_db,
                            top_k=8
                        )

                        # Generate answer
                        answer, sources = generate_answer(
                            user_question,
                            relevant_chunks
                        )

                        # Save assistant response to database
                        save_message(
                            st.session_state.conversation_id,
                            "assistant",
                            answer
                        )

                        # Add bot message to Streamlit chat history
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': answer,
                            'sources': sources
                        })

                    st.rerun()
        
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
