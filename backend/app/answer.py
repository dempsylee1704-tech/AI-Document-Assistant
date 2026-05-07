from openai import OpenAI

from vector_db import search_chunks
from config import API_KEY

client = OpenAI(api_key=API_KEY)

def generate_answer(query, chunks):
    context = ""
    for chunk in chunks:
        context += chunk["text"] + "\n\n"

    prompt = f"""
You are an assistant that answers questions based on provided context.
If the answer is not in the context, say that you cannot find it.
Do not invent information.

Context:
{context}

Question:
{query}

Answer:
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text

def ask_documents(query, doc_id=None):
    results = search_chunks(query, doc_id=doc_id)
    answer = generate_answer(query, results)

    return {
        "answer": answer,
        "sources": results
    }