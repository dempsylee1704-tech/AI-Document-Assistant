from docling.document_converter import DocumentConverter
from pathlib import Path

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



        # Export and save as Markdown
        md = doc.export_to_markdown()
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md)

if __name__ == "__main__":
    main()