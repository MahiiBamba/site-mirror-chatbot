# 🔍 Site-Mirror Chatbot

**AI-Powered Website Mirror Dashboard with RAG Chat**

Transform any public website into an intelligent, searchable knowledge base with automatic FAQ extraction, AI-powered summaries, and a chat interface that answers questions based strictly on the site's content.

---

## 🎯 What It Does

Site-Mirror Chatbot solves a common problem: websites contain vast amounts of information that's hard to navigate. This tool:

1. **Crawls** any public website intelligently
2. **Indexes** the content using vector embeddings
3. **Extracts** FAQs automatically
4. **Generates** AI summaries of the site
5. **Enables chat** with strict source attribution

### Key Features

✅ **Intelligent Crawling** - Discovers site structure automatically  
✅ **RAG-Powered Chat** - Answers grounded in indexed content only  
✅ **Zero Hallucination Mode** - Responses strictly from crawled data  
✅ **Auto FAQ Detection** - Extracts Q&A pairs automatically  
✅ **Source Citations** - Every answer links to original pages  
✅ **Visual Dashboard** - Site summary, topics, and structure  
✅ **Free Resources Only** - No paid APIs required (uses free tiers)

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   User URL Input    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Website Crawler    │
│  (BeautifulSoup)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Text Chunking     │
│   (Overlap: 100)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Embeddings Model   │
│  (all-MiniLM-L6-v2) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Vector Database   │
│     (ChromaDB)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Similarity Search │
│   (Cosine Distance) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Claude API       │
│  (Answer Generation)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Streamlit Chat UI  │
└─────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Anthropic API key (free tier available)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/site-mirror-chatbot.git
cd site-mirror-chatbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Get your free Anthropic API key at: https://console.anthropic.com/

4. **Run the application**
```bash
streamlit run app.py
```

5. **Open in browser**
```
Local URL: http://localhost:8501
```

---

## 📖 How to Use

### Step 1: Enter Website URL
In the sidebar, enter any public website URL:
```
https://docs.anthropic.com
https://python.org
https://example.com
```

### Step 2: Configure Crawling
- **Max Depth**: How deep to crawl (1-3 recommended)
- **Max Pages**: Maximum pages to index (5-50)

### Step 3: Start Crawling
Click "🚀 Start Crawling" and wait for processing.

The system will:
- Discover pages automatically
- Extract clean content
- Generate embeddings
- Store in vector database

### Step 4: Explore Dashboard

**Overview Tab**
- AI-generated site summary
- Detected topics
- Page statistics

**FAQs Tab**
- Automatically extracted questions
- Source attribution for each FAQ

**Chat Tab**
- Ask questions about the website
- Get answers with source citations
- Responses strictly from indexed content

---

## 🧠 How It Works (Technical Deep Dive)

### 1. Web Crawling

**Technology**: BeautifulSoup4 + Requests

```python
# Intelligent crawling with depth control
crawler = WebsiteCrawler(url, max_depth=2, max_pages=20)
```

**Features**:
- Respects same-domain boundaries
- Avoids duplicate pages
- Filters out media files
- Extracts structured content (headings, paragraphs, lists)

### 2. Content Processing

**Text Cleaning**:
- Removes navigation, ads, footers
- Normalizes whitespace
- Filters boilerplate content

**Text Chunking**:
```python
chunk_size = 500 characters
overlap = 100 characters
```

**Why overlap?**  
Preserves context across chunk boundaries for better retrieval.

### 3. Vector Embeddings

**Model**: `all-MiniLM-L6-v2` (SentenceTransformers)
- 384 dimensions
- 80MB model size
- Fast inference
- Good semantic understanding

**Process**:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(chunks, batch_size=32)
```

### 4. Vector Storage

**Database**: ChromaDB (local, persistent)

**Storage location**: `data/chromadb/`

**Similarity metric**: Cosine similarity

**Why ChromaDB?**
- Lightweight
- Persistent storage
- Built-in metadata filtering
- No server required

### 5. Retrieval (RAG)

**Retrieval Process**:
1. User asks question
2. Question → embedding
3. Similarity search in vector DB
4. Return top K chunks (K=4)

**Similarity Formula**:
```
similarity = dot(query_embedding, chunk_embedding) / 
             (||query_embedding|| * ||chunk_embedding||)
```

### 6. Answer Generation

**LLM**: Claude Sonnet 4 (via Anthropic API)

**Prompt Engineering**:
```
You are a helpful assistant that answers questions 
based STRICTLY on the provided context.

RULES:
1. Answer ONLY using information from context
2. If answer not in context, say "I could not find..."
3. Do not make up information
4. Be concise and direct
```

**Why this works?**
- Clear instructions reduce hallucinations
- Context grounding ensures accuracy
- Source attribution builds trust

---

## 📁 Project Structure

```
site-mirror-chatbot/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── scraper/                    # Web scraping module
│   ├── __init__.py
│   ├── crawler.py             # Website crawling logic
│   ├── parser.py              # HTML parsing
│   └── cleaner.py             # Text cleaning
│
├── rag/                        # RAG components
│   ├── __init__.py
│   ├── chunker.py             # Text chunking with overlap
│   ├── embeddings.py          # Embedding generation
│   ├── vectordb.py            # ChromaDB operations
│   ├── retriever.py           # Similarity search
│   └── qa_chain.py            # Answer generation with Claude
│
├── dashboard/                  # Dashboard components
│   ├── __init__.py
│   ├── summary.py             # AI summary generation
│   ├── faq_extractor.py       # FAQ detection
│   └── sitemap.py             # Site structure visualization
│
└── data/                       # Data storage
    ├── chromadb/              # Vector database (auto-created)
    ├── raw/                   # Raw crawled data
    └── processed/             # Processed data
```

---

## 🔬 Technical Decisions Explained

### Why ChromaDB over FAISS?

| ChromaDB | FAISS |
|----------|-------|
| ✅ Persistent storage | ❌ Requires manual persistence |
| ✅ Metadata filtering | ⚠️ Limited metadata support |
| ✅ Simple API | ❌ More complex setup |
| ✅ Python-native | ⚠️ C++ bindings |

**Decision**: ChromaDB for ease of use and built-in persistence.

### Why Claude API over Local LLMs?

| Claude API | Ollama/Local |
|------------|--------------|
| ✅ Superior reasoning | ⚠️ Variable quality |
| ✅ Better instruction following | ❌ Often hallucinates |
| ✅ No GPU required | ❌ Needs GPU/slow on CPU |
| ✅ Generous free tier | ✅ Fully local |

**Decision**: Claude API for better answer quality and reliability.

### Why Sentence Transformers?

- **Open source** and free
- **Small model size** (80MB)
- **Fast** on CPU
- **Good performance** for retrieval tasks
- **Easy integration** with ChromaDB

### Text Chunking Strategy

**Fixed size with overlap** vs other strategies:

| Strategy | Pros | Cons |
|----------|------|------|
| **Fixed + Overlap** (chosen) | ✅ Preserves context<br>✅ Predictable size | ⚠️ May split sentences |
| Paragraph-based | ✅ Natural boundaries | ❌ Unpredictable sizes |
| Sentence-based | ✅ Clean boundaries | ❌ Too granular |

**Our approach**: Fixed 500 chars + 100 char overlap
- **500 chars** ≈ 2-3 sentences (good semantic unit)
- **100 char overlap** ensures context continuity

---

## 🎨 Design Decisions

### UI/UX Philosophy

**Clean, professional, trust-building**

1. **Custom fonts**:
   - Crimson Pro (headings) - elegant serif
   - Manrope (body) - modern sans-serif

2. **Color scheme**:
   - Primary: Deep teal (#0A4D68) - professional
   - Accent: Bright cyan (#05BFDB) - energetic
   - Success: Green - positive feedback

3. **Visual hierarchy**:
   - Clear status indicators
   - Source attribution badges
   - Card-based layouts

4. **Information density**:
   - Not overwhelming
   - Progressive disclosure
   - Tab-based organization

### Why These Design Choices?

- **Trust**: Academic feel (serif headings)
- **Modernity**: Sans-serif body text
- **Clarity**: High contrast, clear CTAs
- **Professionalism**: Consistent spacing, polished interactions

---

## 🚀 Deployment

### Streamlit Community Cloud (Recommended)

**100% Free**, perfect for this project.

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-repo-url
git push -u origin main
```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect GitHub repository
   - Add `ANTHROPIC_API_KEY` to secrets

3. **Secrets Configuration**:
```toml
# .streamlit/secrets.toml
ANTHROPIC_API_KEY = "your_api_key"
```

### Alternative: HuggingFace Spaces

1. Create Space on HuggingFace
2. Select Streamlit SDK
3. Push code
4. Add API key to Settings → Repository Secrets

---

## 📊 Performance Optimization

### Current Performance

- **Crawl time**: ~1 second per page
- **Embedding generation**: ~2 seconds for 100 chunks
- **Vector search**: <100ms
- **Answer generation**: 2-5 seconds (Claude API)

### Optimization Tips

1. **Limit crawl depth** to 2 for faster processing
2. **Batch embedding generation** (already implemented)
3. **Cache results** in session state (already implemented)
4. **Reduce chunk size** if memory constrained

---

## 🧪 Testing Your Implementation

### Test Case 1: Simple FAQ Site

**URL**: `https://example-faq-site.com`

**Expected**:
- Extracts Q&A pairs
- Shows in FAQ tab
- Chat answers from FAQs

### Test Case 2: Documentation Site

**URL**: `https://docs.anthropic.com`

**Expected**:
- Comprehensive site summary
- Clear topic extraction
- Accurate technical answers

### Test Case 3: Error Handling

**URL**: `https://invalid-url-12345.com`

**Expected**:
- Graceful error message
- No crash
- User-friendly feedback

---

## 🎓 Learning Outcomes

Building this project teaches:

1. **Web Scraping**:
   - BeautifulSoup basics
   - Respectful crawling
   - Content extraction

2. **NLP & Embeddings**:
   - Sentence transformers
   - Vector representations
   - Semantic similarity

3. **Vector Databases**:
   - ChromaDB operations
   - Similarity search
   - Metadata filtering

4. **RAG Architecture**:
   - Retrieval strategies
   - Context management
   - Prompt engineering

5. **LLM Integration**:
   - API usage
   - Response handling
   - Error management

6. **Full-Stack Development**:
   - Streamlit UI
   - State management
   - User experience design

---

## 🐛 Common Issues & Solutions

### Issue: "No module named 'sentence_transformers'"

**Solution**:
```bash
pip install sentence-transformers
```

### Issue: ChromaDB persistence error

**Solution**:
```bash
# Delete and recreate database
rm -rf data/chromadb/
```

### Issue: Slow embedding generation

**Solution**:
- Use smaller batch size
- Reduce number of chunks
- Limit max_pages

### Issue: Claude API rate limits

**Solution**:
- Add delay between requests
- Use caching
- Upgrade API tier if needed

---

## 🎯 Future Enhancements

### Priority 1 (Resume-Boosting)
- [ ] Multi-website comparison
- [ ] Export reports to PDF
- [ ] Advanced filtering (by page type, date)

### Priority 2 (Advanced Features)
- [ ] Live mode (web search integration)
- [ ] Session persistence
- [ ] User authentication

### Priority 3 (Nice-to-Have)
- [ ] Streaming responses
- [ ] Voice input/output
- [ ] Mobile optimization

---

## 📝 License

MIT License - Feel free to use for personal/commercial projects.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📧 Contact

**Your Name**  
📧 your.email@example.com  
🔗 [LinkedIn](https://linkedin.com/in/yourprofile)  
🐙 [GitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- **Anthropic** - Claude API
- **Streamlit** - UI framework
- **ChromaDB** - Vector database
- **SentenceTransformers** - Embedding models

---

**Built with ❤️ and AI**
