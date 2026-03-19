from qdrant_client import QdrantClient
from config import QDRANT_URL, QDRANT_API_KEY
from qdrant_client.models import VectorParams, Distance, PointStruct
from embeddings import create_embedding


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

def create_collection(collection_name="documents"):
    collections = client.get_collections().collections
    existing_names = [c.name for c in collections]
    if collection_name in existing_names:
        return f"Collection '{collection_name}' already exits."


    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE
        )
    )

    return f"Collection '{collection_name}' created."

def upload_chunks(chunks, collection_name="documents"):
    points = []

    for i, chunk in enumerate(chunks):
        point = PointStruct(
            id=i,
            vector=chunk["embedding"],
            payload={
                "text": chunk["text"],
                "category": chunk.get("category"),
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end")
            }
        )

        points.append(point)

    client.upsert(
        collection_name=collection_name,
        points=points
    )

    return f"{len(points)} chunks uploaded."

def search_chunks(query, collection_name="documents", k=3):
    query_vector = create_embedding(query)

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=k
    )

    chunks = []

    for r in results.points:
        chunks.append(r.payload)

    return chunks