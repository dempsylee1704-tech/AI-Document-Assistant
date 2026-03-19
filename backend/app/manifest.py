from datetime import datetime

def build_manifest(doc_id, pdf_file, doc_data, chunks):
    pages_dict = doc_data.get("pages", {})
    texts_lists = doc_data.get("texts", [])

    manifest = {
        "doc_id": doc_id,
        "source_filename": pdf_file.name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "counts": {
            "pages": len(pages_dict),
            "text_blocks": len(texts_lists),
            "chunks": len(chunks)
    },
        "files": {
            "doc_md": "doc.md",
            "doc_json": "doc.json",
            "chunks_json": "chunks.json",
            "manifest_json": "manifest.json",
            "chunks_enriched_json": "chunks_enriched.json",
            "chunks_with_embeddings_json": "chunks_with_embeddings.json"
        }
    }

    return manifest