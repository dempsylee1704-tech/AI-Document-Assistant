from embeddings import create_embedding
import math

def embed_query(query):
    if not query:
        return None

    else:
        return create_embedding(query)

def cosine_similarity(vec1, vec2):
    if not vec1 or not vec2:
        return 0.0

    if len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)

def find_top_k_chunks(query, embedded_chunks, k=3):
    query_embedding = embed_query(query)
    scored_chunks = []

    for chunk in embedded_chunks:
        chunk_embedding = chunk.get("embedding")
        score = cosine_similarity(query_embedding, chunk_embedding)
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    top_chunks = scored_chunks[:k]
    return [chunk for score, chunk in top_chunks]