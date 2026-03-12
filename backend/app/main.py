from docling.document_converter import DocumentConverter
import json
from chunker import merge_blocks_to_chunks
from extractor import extract_text_blocks
from manifest import build_manifest
from io_utils import list_pdf_files
from config import PROCESSED_DIR, CHUNK_CHAR_SIZE, CHUNK_CHAR_OVERLAP
from metadata_ai import enrich_chunk_metadata
from embeddings import create_embbeddings_for_chunks

def main():
    # Convert PDF to Markdown
    pdf_files = list_pdf_files()
    converter = DocumentConverter()
    for pdf_file in pdf_files:
        doc_id = pdf_file.stem
        out_dir = PROCESSED_DIR / doc_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "doc.md"
        result = converter.convert(pdf_file)
        doc = result.document

        # Export and save as JSON
        out_json = out_dir / "doc.json"
        doc_data = doc.model_dump()

        blocks = extract_text_blocks(doc_data)
        chunks = merge_blocks_to_chunks(blocks, CHUNK_CHAR_SIZE, CHUNK_CHAR_OVERLAP)

        print(doc_id, len(blocks), "blocks ->", len(chunks), "chunks")
        print("first chunk length:", len(chunks[0]["text"]))


        enriched_chunks = []
        for chunk in chunks:
            enriched_chunk = enrich_chunk_metadata(chunk)
            enriched_chunks.append(enriched_chunk)

        embedded_chunks = create_embbeddings_for_chunks(enriched_chunks)

        out_embedded_chunks = out_dir / "chunks_with_embeddings.json"

        with open(out_embedded_chunks, "w", encoding="utf-8") as f:
            json.dump(embedded_chunks, f, indent=2, ensure_ascii=False)

        out_enriched_chunks = out_dir / "chunks_enriched.json"

        with open(out_enriched_chunks, "w", encoding="utf-8") as f:
            json.dump(enriched_chunks, f, indent=2, ensure_ascii=False)

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)

        out_chunks = out_dir / "chunks.json"
        print(doc_id, "Chunks:", len(chunks))

        with open(out_chunks, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        manifest = build_manifest(doc_id, pdf_file, doc_data, chunks)

        out_manifest = out_dir / "manifest.json"
        with open(out_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)



        # Export and save as Markdown
        md = doc.export_to_markdown()
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md)

if __name__ == "__main__":
    main()