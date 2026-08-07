from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType

from config import QDRANT_URL, QDRANT_API_KEY, PUBLIC_BASE_URL
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from embeddings import create_embedding
import uuid


def get_qdrant_client():
    if not QDRANT_URL:
        raise RuntimeError("QDRANT_URL is not configured.")
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )

def create_collection(collection_name="documents"):
    client = get_qdrant_client()
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
    client = get_qdrant_client()
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

def search_chunks(query, collection_name="documents", k=8, doc_id=None):
    client = get_qdrant_client()
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
        page = r.payload.get("page_start") or r.payload.get("page_no") or 1

        result_chunk = {
            **r.payload,
            "score": r.score,
            "page": page,
            "pdf_url": f"{PUBLIC_BASE_URL}/pdf/{r.payload['doc_id']}#page={page}",
        }

        chunks.append(result_chunk)

    return chunks

def create_payload_indexes(collection_name="documents"):
    client = get_qdrant_client()
    client.create_payload_index(
        collection_name=collection_name,
        field_name="doc_id",
        field_schema=PayloadSchemaType.KEYWORD
    )

    return "Payload index for doc_id created."

def delete_collection(collection_name="documents"):
    client = get_qdrant_client()
    client.delete_collection(collection_name=collection_name)
    return f"Collection {collection_name} deleted."
