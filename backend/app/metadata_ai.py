import json
import time

from openai import OpenAI, RateLimitError
from config import API_KEY


client = OpenAI(api_key=API_KEY)

categories = ["contract",
             "form",
             "presentation",
             "policy",
             "report",
             "invoice",
             "other"]

def enrich_chunk_metadata(chunk):
    text = chunk["text"]
    prompt = f"""
    You are an AI system that analyzes document sections.
    
    Analyze the following document section.
    
        Extract:
    - summary (one sentence)
    - keywords (3 to 5)
    - category

    Use only one of these categories:
    contract, form, presentation, policy, invoice, report, other

    Return ONLY valid JSON with these fields:
    summary must be a string
    keywords must be a list
    category in string but only from {categories}

    Document section:
    {text}"""

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )

    except RateLimitError:
        print("OpenAI rate limit reached. Using fallback metadata.")

        return {
            "summary": "Metadata could not be generated due to rate limit.",
            "keywords": [],
            "category": "other"
        }

    except Exception as e:
        print(f"Metadata enrichment failed: {e}")

        return {
            "summary": "Metadata could not be generated.",
            "keywords": [],
            "category": "other"
        }

    response_text = response.output_text

    clean_text = response_text.removeprefix("```json").removesuffix("```").strip()


    result = json.loads(clean_text)


    try:
        summary = result.get("summary")
        keywords = result.get("keywords", [])
        category = result.get("category", "other")

    except:
        summary = None
        keywords = []
        category = "other"

    if category not in categories:
        category = "other"

    if not isinstance(keywords, list):
        keywords = []

    enriched_chunk = {"text": chunk["text"],
                      "page_start": chunk["page_start"],
                      "page_end": chunk["page_end"],
                      "summary": summary,
                      "keywords": keywords,
                      "category": category}

    return enriched_chunk



