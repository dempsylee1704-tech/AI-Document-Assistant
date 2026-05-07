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
            label = item

            if "_" in item:
                possible_uuid, rest = item.split("_", 1)
                if len(possible_uuid) > 20:
                    label = rest

            documents.append({
                "doc_id": item,
                "label": label
            })

    return documents

def get_pdf_path_by_doc_id(doc_id: str):
    # exakter Match
    pdf_path = RAW_DIR / f"{doc_id}.pdf"
    if pdf_path.exists():
        return pdf_path

    # falls .pdf schon dran ist
    pdf_path = RAW_DIR / doc_id
    if pdf_path.exists():
        return pdf_path

    # robuster Fallback: UUID vorne nehmen und passende PDF suchen
    uuid_part = doc_id.split("_")[0]
    matches = list(RAW_DIR.glob(f"{uuid_part}*.pdf"))

    if matches:
        return matches[0]

    return None