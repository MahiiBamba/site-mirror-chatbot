

from typing import Dict, List
import ollama


def generate_site_summary(crawl_data: Dict) -> Dict:
    
    pages = crawl_data.get("pages", [])

    if not pages:
        return {
            "title": "No content",
            "summary": "No pages were crawled.",
            "topics": []
        }

    sample_content = []

    for page in pages[:5]:
        title = page.get("title", "")
        text = page.get("text", "")[:1000]

        if title and text:
            sample_content.append(
                f"Title: {title}\n{text}"
            )

    content_text = "\n\n".join(sample_content)

    prompt = f"""
Analyze this website content and generate:

1. A concise summary (100-150 words)
2. 5 main topics

Website Content:

{content_text}

Return in this format:

SUMMARY:
<summary>

TOPICS:
- topic1
- topic2
- topic3
- topic4
- topic5
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

        output = response["message"]["content"]

        summary = output
        topics = []

        if "TOPICS:" in output:
            parts = output.split("TOPICS:")

            summary = (
                parts[0]
                .replace("SUMMARY:", "")
                .strip()
            )

            topics_text = parts[1]

            topics = [
                line.replace("-", "").strip()
                for line in topics_text.split("\n")
                if line.strip().startswith("-")
            ]

        return {
            "title": pages[0].get(
                "title",
                "Website"
            ),
            "summary": summary,
            "topics": topics
        }

    except Exception as e:

        return {
            "title": pages[0].get(
                "title",
                "Website"
            ),
            "summary": f"Error generating summary: {e}",
            "topics": []
        }


def extract_key_pages(
    crawl_data: Dict
) -> List[Dict]:
    

    pages = crawl_data.get("pages", [])

    key_pages = sorted(
        pages,
        key=lambda x: x.get(
            "depth",
            999
        )
    )[:10]

    return [
        {
            "title": page.get(
                "title",
                "Untitled"
            ),
            "url": page.get(
                "url",
                ""
            ),
            "depth": page.get(
                "depth",
                0
            )
        }
        for page in key_pages
    ]