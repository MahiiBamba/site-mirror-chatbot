

import sys, os, uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from database import (
    create_conversation,
    save_message,
    format_conversation_history
)


sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.crawler    import crawl_website
from rag.vectordb       import store_embeddings
from rag.retriever      import retrieve_relevant_chunks
from rag.qa_chain       import generate_answer, rewrite_query
from rag.chunker        import chunk_documents
from rag.embeddings     import generate_embeddings
from dashboard.summary  import generate_site_summary
from dashboard.faq_extractor import extract_faqs
from database import format_conversation_history


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "site-mirror-dev-secret")


_store: dict = {}

def _sd() -> dict:
    """Return (or create) per-session data bucket."""
    sid = session.get("sid")
    if not sid:
        sid = str(uuid.uuid4())
        session["sid"] = sid
    if sid not in _store:

        conversation_id = create_conversation()

        _store[sid] = {
            "crawl_data": None,
            "vector_db": None,
            "chat_history": [],
            "conversation_id": conversation_id,
            "crawl_status": "idle",
            "site_summary": None,
            "faqs": None,
        }
    return _store[sid]




@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/dashboard")
@app.route("/dashboard/")
@app.route("/dashboard/<path:sub>")
def dashboard(sub=None):
    data = _sd()

    print("CONVERSATION ID:", data["conversation_id"])

    return render_template(
        "dashboard.html",
        status=data["crawl_status"]
    )




@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    data = _sd()
    body      = request.get_json(force=True)
    url       = body.get("url", "").strip()
    max_depth = int(body.get("max_depth", 2))
    max_pages = int(body.get("max_pages", 20))

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        data["crawl_status"] = "processing"

        crawl_results          = crawl_website(url, max_depth=max_depth, max_pages=max_pages)
        data["crawl_data"]     = crawl_results
        data["site_summary"]   = None
        data["faqs"]           = None
        data["chat_history"]   = []

        chunks         = chunk_documents(crawl_results["pages"])
        embeddings_data = generate_embeddings(chunks)
        vector_db      = store_embeddings(embeddings_data, url)
        data["vector_db"]    = vector_db
        data["crawl_status"] = "complete"

        return jsonify({
            "status":       "complete",
            "pages_indexed": len(crawl_results["pages"]),
            "total_links":   len(crawl_results["all_links"]),
            "chunks_total":  len(chunks),
            "sitemap": [
                {"url": p["url"], "title": p.get("title",""), "depth": p.get("depth",0)}
                for p in crawl_results["pages"]
            ],
        })

    except Exception as exc:
        data["crawl_status"] = "idle"
        return jsonify({"error": str(exc)}), 500


@app.route("/api/summary")
def api_summary():
    data = _sd()
    if data["crawl_status"] != "complete":
        return jsonify({"error": "No crawled data"}), 400
    if data["site_summary"] is None:
        try:
            data["site_summary"] = generate_site_summary(data["crawl_data"])
        except Exception:
            data["site_summary"] = {"title":"Website Overview","summary":"Summary unavailable.","topics":[]}
    s = data["site_summary"]
    return jsonify({
        "title":         s.get("title",""),
        "summary":       s.get("summary",""),
        "topics":        s.get("topics",[]),
        "pages_indexed": len(data["crawl_data"]["pages"]),
        "total_links":   len(data["crawl_data"]["all_links"]),
    })


@app.route("/api/faqs")
def api_faqs():
    data = _sd()
    if data["crawl_status"] != "complete":
        return jsonify({"error": "No crawled data"}), 400
    if data["faqs"] is None:
        data["faqs"] = extract_faqs(data["crawl_data"])
    return jsonify({"faqs": data["faqs"] or []})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = _sd()
    if data["crawl_status"] != "complete" or data["vector_db"] is None:
        return jsonify({"error": "Please crawl a website first"}), 400
    body     = request.get_json(force=True)
    question = body.get("question","").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400

    save_message(
        data["conversation_id"],
        "user",
        question
    )


    history = format_conversation_history(
        data["conversation_id"]
    )

    rewritten_question = rewrite_query(
        question,
        history
    )

    print("ORIGINAL QUESTION:", question)
    print("REWRITTEN QUESTION:", rewritten_question)

    chunks          = retrieve_relevant_chunks(rewritten_question, data["vector_db"], top_k=8)
    answer, sources = generate_answer(rewritten_question, chunks)
    save_message(
        data["conversation_id"],
        "assistant",
        answer
    )

    data["chat_history"].append({"role":"user",      "content": question})
    data["chat_history"].append({"role":"assistant", "content": answer, "sources": sources})

    return jsonify({"answer": answer, "sources": sources, "history": data["chat_history"]})


@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    _sd()["chat_history"] = []
    return jsonify({"ok": True})


@app.route("/api/status")
def api_status():
    data = _sd()
    stats = {}
    if data["crawl_data"]:
        stats["pages"]  = len(data["crawl_data"]["pages"])
        stats["links"]  = len(data["crawl_data"]["all_links"])
    return jsonify({"status": data["crawl_status"], **stats})


if __name__ == "__main__":
    app.run(debug=True, port=5000)