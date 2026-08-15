
# Site-Mirror

> **Chat with any website using AI — powered by RAG and local LLM inference.**

Site-Mirror turns a website into an interactive AI assistant. It crawls the website, extracts and chunks its content, creates embeddings, stores them in ChromaDB, and uses semantic retrieval + a local Llama model through Ollama to answer questions.

## ✨ Features

- 🌐 Recursive website crawling with BeautifulSoup
- ✂️ Text cleaning and chunking
- 🧠 Semantic embeddings using `all-MiniLM-L6-v2`
- 🗄️ ChromaDB vector storage
- 🔎 Semantic search and relevant-context retrieval
- 🤖 Local Llama inference through Ollama
- 💬 Context-aware AI chat with follow-up questions
- ❓ Automatic FAQ generation
- 📋 Website summaries
- 🗺️ Sitemap visualization
- 📊 Interactive crawling dashboard

## 🔄 RAG Pipeline

```text
Website URL
    ↓
Web Crawler
    ↓
HTML → Clean Text
    ↓
Text Chunking
    ↓
Sentence Embeddings
    ↓
ChromaDB
    ↓
Semantic Retrieval
    ↓
Relevant Context
    ↓
Local Llama + Ollama
    ↓
Grounded AI Response
```

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| BeautifulSoup4 | Web crawling & HTML parsing |
| Sentence Transformers | Text embeddings |
| ChromaDB | Vector database |
| Ollama | Local LLM runtime |
| Llama3.1 8b | Answer generation |

## 📁 Main Modules

```text
crawler.py          → Website crawling
vector_db.py        → ChromaDB operations
retriever.py        → Semantic retrieval
qa_chain.py         → Local LLM / RAG pipeline
faq_extractor.py    → FAQ generation
summary.py          → Website summary
sitemap.py          → Sitemap visualization
app.py              → Application interface
```

## 🖥️ Screenshots

### Landing Page

![Site-Mirror Homepage](assets/01-homepage.png)

### Pipeline Modules

![Pipeline Modules](assets/02-pipeline-modules.png)

### RAG Pipeline

![RAG Pipeline](assets/03-rag-pipeline.png)

### Crawling Dashboard

![Crawling Dashboard](assets/04-crawling-console.png)

### AI Chat

![AI Chat](assets/05-ai-chat.png)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MahiiBamba/site-mirror-chatbot.git
cd <site-mirror-chatbot>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Ollama

```bash
ollama serve
ollama pull llama3.1:8b
```

### 4. Run the application

Use the project's configured entry point, for example:

```bash
python app.py
```

## 🎯 Why Site-Mirror?

Site-Mirror demonstrates how **web crawling, embeddings, vector databases, semantic retrieval, and local LLMs** can be combined to build a practical **Retrieval-Augmented Generation (RAG)** system.

The project also makes the individual stages of the pipeline visible instead of hiding everything behind a simple chatbot.

## 🔮 Future Improvements

- Hybrid search and re-ranking
- Better JavaScript-heavy website support
- Persistent conversation history
- Multi-website knowledge bases
- Docker deployment
- Retrieval and answer-quality evaluation

## 📄 License

Add your preferred license here.