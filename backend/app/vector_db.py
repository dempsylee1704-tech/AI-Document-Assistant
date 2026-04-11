from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType

from config import QDRANT_URL, QDRANT_API_KEY
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from embeddings import create_embedding
import uuid


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

def upload_chunks(chunks, doc_id, source_filename, collection_name="documents"):
    points = []

    for i, chunk in enumerate(chunks):
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=chunk["embedding"],
            payload={
                "text": chunk["text"],
                "category": chunk.get("category"),
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
                "doc_id": doc_id,
                "source_filename": source_filename
            }
        )

        points.append(point)

    client.upsert(
        collection_name=collection_name,
        points=points
    )

    return f"{len(points)} chunks uploaded."

def search_chunks(query, collection_name="documents", k=3, doc_id=None):
    query_vector = create_embedding(query)

    if doc_id:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="doc_id",
                    match=MatchValue(value=doc_id)
                )
            ]
        )

        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=k
        )
    else:
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=k
        )

    chunks = []

    for r in results.points:
        result_chunk = {
            **r.payload,
            "score": r.score
        }
        chunks.append(result_chunk)

    return chunks

def create_payload_indexes(collection_name="documents"):
    client.create_payload_index(
        collection_name=collection_name,
        field_name="doc_id",
        field_schema=PayloadSchemaType.KEYWORD
    )

    return "Payload index for doc_id created."

def delete_collection(collection_name="documents"):
    client.delete_collection(collection_name=collection_name)
    return f"Collection {collection_name} deleted."