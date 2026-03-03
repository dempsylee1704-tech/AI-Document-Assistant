from docling.document_converter import DocumentConverter
from pathlib import Path
import json
from datetime import datetime

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

def list_pdf_files(raw_dir: Path = RAW_DIR) -> list[Path]:
    # Checks if folder exists
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw directory not found: {raw_dir.resolve()}")

    # Find all PDF's
    pdfs = [p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]

    # Sort PDF's
    pdfs.sort(key=lambda p: p.name.lower())
    return pdfs


def extract_text_blocks(doc_data):
    blocks = []
    for block in doc_data["texts"]:
        text = block.get("text", "")
        label = block.get("label")
        prov = block.get("prov")
        if prov:
            page_no = prov[0].get("page_no")
        else:
            page_no = None

        if not text.strip():
            continue

        blocks.append({
            "text": text,
            "label": label,
            "page_no": page_no
        })

    return  blocks

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
            "manifest_json": "manifest.json"
        }
    }

    return manifest

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

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)

        chunks = extract_text_blocks(doc_data)
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