from pathlib import Path
from config import RAW_DIR, PROCESSED_DIR
import os

def list_pdf_files(raw_dir: Path = RAW_DIR) -> list[Path]:
    # Checks if folder exists
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw directory not found: {raw_dir.resolve()}")

    # Find all PDF's
    pdfs = [p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]

    # Sort PDF's
    pdfs.sort(key=lambda p: p.name.lower())
    return pdfs

def list_processed_documents():
    documents = []

    for item in os.listdir(PROCESSED_DIR):
        path = os.path.join(PROCESSED_DIR, item)

        if os.path.isdir(path):
            documents.append(item)

    return documents