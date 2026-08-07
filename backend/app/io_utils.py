from pathlib import Path
from config import RAW_DIR, PROCESSED_DIR
import os
import re

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
    seen_labels = set()

    for item in os.listdir(PROCESSED_DIR):
        path = os.path.join(PROCESSED_DIR, item)

        if not os.path.isdir(path):
            continue

        manifest_path = os.path.join(path, "manifest.json")

        # Nur Dokumente anzeigen, die wirklich fertig verarbeitet wurden
        if not os.path.exists(manifest_path):
            continue

        label = item

        # Wenn vorne eine UUID steht, für die Anzeige entfernen
        if "_" in item:
            possible_uuid, rest = item.split("_", 1)
            if len(possible_uuid) > 20:
                label = rest

        # Dateiendung für schöneren Namen entfernen
        if label.lower().endswith(".pdf"):
            label = label[:-4]

        # Doppelte Anzeigenamen überspringen
        normalized_label = label.strip().lower()

        if normalized_label in seen_labels:
            continue

        seen_labels.add(normalized_label)

        documents.append({
            "doc_id": item,
            "label": label
        })

    documents.sort(key=lambda d: d["label"].lower())

    return documents

def get_pdf_path_by_doc_id(doc_id: str):
    # Reject path traversal and malformed IDs before touching the filesystem.
    if Path(doc_id).name != doc_id or not re.fullmatch(r"[A-Za-z0-9._-]+", doc_id):
        return None

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
