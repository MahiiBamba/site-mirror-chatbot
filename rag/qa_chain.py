"""
QA Chain
Generate answers using local Ollama Llama model and retrieved context
"""

from typing import List, Dict, Tuple
import ollama


def create_rag_prompt(query: str, context_chunks: List[Dict]) -> str:
    """
    Create formatted context for RAG
    """

    context_parts = []

    for i, chunk in enumerate(context_chunks, 1):
        source = chunk["metadata"].get("source_url", "Unknown")
        title = chunk["metadata"].get("title", "Untitled")
        text = chunk["text"]

        context_parts.append(
            f"""
Source {i}
Title: {title}
URL: {source}

Content:
{text}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a helpful website assistant.

Answer the user's question ONLY using the provided context.

Rules:
- Answer only from the context.
- If information is missing, explicitly say so.
- Combine information from multiple context chunks when needed.
- Do not repeat the context verbatim.
- Keep answers under 150 words unless asked otherwise.

Context:
{context}

Question:
{query}

Answer:
"""

    return prompt


def generate_answer(
    query: str,
    context_chunks: List[Dict]
) -> Tuple[str, List[str]]:
    """
    Generate answer using local Ollama Llama
    """

    if not context_chunks:
        return (
            "I could not find any relevant information to answer your question.",
            []
        )

    try:

        prompt = create_rag_prompt(query, context_chunks)

        # Debug
        print("\n" + "=" * 80)
        print("QUESTION:", query)
        print("=" * 80)

        for i, chunk in enumerate(context_chunks):
            print(f"\nCHUNK {i+1}")
            print(f"Distance: {chunk['distance']}")
            print(chunk["text"][:500])

        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response["message"]["content"]

        sources = list(
            set(
                [
                    chunk["metadata"].get(
                        "source_url",
                        "Unknown"
                    )
                    for chunk in context_chunks
                ]
            )
        )

        return answer, sources

    except Exception as e:
        return (
            f"Error generating answer: {str(e)}",
            []
        )


def generate_streaming_answer(
    query: str,
    context_chunks: List[Dict]
):
    """
    Streaming answer using Ollama
    """

    if not context_chunks:
        yield "I could not find any relevant information to answer your question."
        return

    try:

        prompt = create_rag_prompt(
            query,
            context_chunks
        )

        stream = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        for chunk in stream:
            yield chunk["message"]["content"]

    except Exception as e:
        yield f"Error generating answer: {str(e)}"



def rewrite_query(query: str, history: str) -> str:
    """
    Rewrite the current question using conversation history
    so it can be understood independently.
    """

    if not history:
        return query

    prompt = f"""
You are a query rewriting assistant for a website question-answering system.

Your ONLY task is to rewrite the CURRENT QUESTION into a standalone
question for semantic search.

IMPORTANT RULES:

1. Preserve the CURRENT QUESTION's exact meaning and intent.
2. Use conversation history ONLY to resolve references such as:
   "it", "they", "this", "that", "which one", "what about", etc.
3. NEVER infer, assume, or invent facts.
4. NEVER introduce categories, technologies, names, entities, or details
   that are not explicitly present in the conversation.
5. Preserve important terms from the CURRENT QUESTION, such as
   "backend", "frontend", "price", "refund", "location", etc.
6. If a reference cannot be resolved confidently, keep the reference
   or make the smallest possible clarification.
7. If the CURRENT QUESTION is already standalone, return it unchanged.
8. Do NOT answer the question.
9. Return ONLY the rewritten question.

Conversation history:
{history}

CURRENT QUESTION:
{query}

STANDALONE QUESTION:
"""

    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        rewritten_query = response["message"]["content"].strip()

        return rewritten_query

    except Exception:
        return query