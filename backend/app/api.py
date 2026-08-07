import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from config import ALLOWED_ORIGINS, API_KEY, MAX_UPLOAD_SIZE, QDRANT_URL, RAW_DIR
from io_utils import list_processed_documents, get_pdf_path_by_doc_id
from pydantic import BaseModel
from answer import ask_documents
from main import ingest_pdf_file
from typing import  List

app = FastAPI(
    title="AI Document Assistant API",
    description="Upload PDF documents and ask source-grounded questions about their content.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    query: str
    doc_id: str | None = None

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "services": {
            "openai_configured": bool(API_KEY),
            "qdrant_configured": bool(QDRANT_URL),
        },
    }

@app.get("/documents")
def get_documents():
    docs = list_processed_documents()
    return {"documents": docs}

@app.post("/ask")
def ask_question(request: AskRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Question must not be empty.")
    try:
        return ask_documents(query, request.doc_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The document service is currently unavailable.") from exc

def validate_pdf(file: UploadFile) -> str:
    filename = Path(file.filename or "document.pdf").name
    if not filename.lower().endswith(".pdf") or file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    if file.size is not None and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="PDF files must not exceed 25 MB.")
    return filename

@app.post("/upload")
async def upload_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File()
        ):

    filename = validate_pdf(file)
    unique_name = f"{uuid4()}_{filename}"
    file_path = RAW_DIR / unique_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(ingest_pdf_file, file_path)
        
    return {
        "message": "File uploaded successfully.",
        "filename": unique_name,
        "status": "processing"
    }

@app.post("/upload-multiple")
async def upload_multiple_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    uploaded_files = []
    rejected_files = []

    for file in files:
        try:
            filename = validate_pdf(file)
        except HTTPException as exc:
            rejected_files.append({
                "filename": file.filename,
                "reason": exc.detail
            })
            continue

        unique_name = f"{uuid4()}_{filename}"
        file_path = RAW_DIR / unique_name

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        background_tasks.add_task(ingest_pdf_file, file_path)

        uploaded_files.append({
            "filename": file.filename,
            "stored_filename": unique_name,
            "status": "processing"
        })

    if not uploaded_files and rejected_files:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No valid PDF files uploaded.",
                "rejected_files": rejected_files
            }
        )

    return {
        "message": "Upload started.",
        "uploaded_files": uploaded_files,
        "rejected_files": rejected_files}

@app.get("/pdf/{doc_id:path}")
def get_pdf(doc_id: str):
    pdf_path = get_pdf_path_by_doc_id(doc_id)

    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found.")

    return FileResponse(pdf_path, media_type="application/pdf")
