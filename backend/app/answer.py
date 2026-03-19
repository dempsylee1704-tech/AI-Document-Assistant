from openai import OpenAI
from config import API_KEY

client = OpenAI(api_key=API_KEY)

def generate_answer(query, chunks):
    context = ""
    for chunk in chunks:
        context += chunk["text"] + "\n\n"

    prompt = f"""
You are an assistant that answers questions based on provided context.

Context:
{context}

Question:
{query}

Answer:
"""

    respone = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return respone.output_text