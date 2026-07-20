from docling.document_converter import DocumentConverter
import json

from chunker import merge_blocks_to_chunks
from extractor import extract_text_blocks
from manifest import build_manifest
from io_utils import list_pdf_files, list_processed_documents
from config import PROCESSED_DIR, CHUNK_CHAR_SIZE, CHUNK_CHAR_OVERLAP
from metadata_ai import enrich_chunk_metadata
from embeddings import create_embeddings_for_chunks
from answer import ask_documents
from vector_db import create_collection, upload_chunks, create_payload_indexes, delete_collection

def ingest_pdf_file(pdf_file):
    converter = DocumentConverter()

    doc_id = pdf_file.stem
    out_dir = PROCESSED_DIR / doc_id
    manifest_path = out_dir / "manifest.json"

    if manifest_path.exists():
        print(f"Skipping {pdf_file.name}, already processed.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    result = converter.convert(pdf_file)
    doc = result.document

    # Export JSON
    out_json = out_dir / "doc.json"
    doc_data = doc.model_dump()

    blocks = extract_text_blocks(doc_data)
    chunks = merge_blocks_to_chunks(blocks, CHUNK_CHAR_SIZE, CHUNK_CHAR_OVERLAP)

    enriched_chunks = []

    for chunk in chunks:
        metadata = enrich_chunk_metadata(chunk)

        enriched_chunk = {
            **chunk,
            **metadata
        }

        enriched_chunks.append(enriched_chunk)

    embedded_chunks = create_embeddings_for_chunks(enriched_chunks)

    create_collection()
    create_payload_indexes()

    upload_chunks(
        embedded_chunks,
        doc_id=doc_id,
        source_filename=pdf_file.name
    )

    # Save files
    with open(out_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, indent=2, ensure_ascii=False)

    manifest = build_manifest(doc_id, pdf_file, doc_data, chunks)

    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"{doc_id} processed successfully.")

def ingest_documents():
    pdf_files = list_pdf_files()

    for pdf_file in pdf_files:
        ingest_pdf_file(pdf_file)

def query_documents():
    docs = list_processed_documents()

    print("\nAvailable documents:")
    for d in docs:
        print("-", d)

    query = input("Question: ")
    doc_id = input("Document ID (optional): ")

    if not doc_id.strip():
        doc_id = None

    result = ask_documents(query, doc_id)

    print("\nANSWER:\n")
    print(result["answer"])

    print("\nSOURCES:\n")

    for r in result["sources"]:
        print(r["doc_id"],
              r["source_filename"],
              r["page_start"],
              r["page_end"],
              r["score"])

def main():
    choice = input("Choose mode: ingest (i) or query (q): ")

    if choice == "i":
        ingest_documents()
    elif choice == "q":
        query_documents()
    elif choice == "d":
        delete_collection()

if __name__ == "__main__":
    main()