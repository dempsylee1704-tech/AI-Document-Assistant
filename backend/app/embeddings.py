from openai import OpenAI
from config import API_KEY

client = OpenAI(api_key=API_KEY)

def create_embedding(text):
    if not text or not text.strip():
        return None

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding

def create_embbeddings_for_chunks(chunks):
    embedded_chunks = []
    for chunk in chunks:
        text = chunk.get("text")
        embedding = create_embedding(text)
        embedded_chunk = {
            **chunk,
            "embedding": embedding
        }

        embedded_chunks.append(embedded_chunk)
    return embedded_chunks


