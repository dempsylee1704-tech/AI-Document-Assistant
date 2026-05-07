import shutil
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from config import RAW_DIR
from io_utils import list_processed_documents, get_pdf_path_by_doc_id
from pydantic import BaseModel
from answer import ask_documents
from main import ingest_pdf_file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class AskRequest(BaseModel):
    query: str
    doc_id: str | None = None

@app.get("/documents")
def get_documents():
    docs = list_processed_documents()
    return {"documents": docs}

@app.post("/ask")
def ask_question(request: AskRequest):
    result = ask_documents(request.query, request.doc_id)
    return result

@app.post("/upload")
async def upload_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File()
        ):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    unique_name = f"{uuid4()}_{file.filename}"
    file_path = RAW_DIR / unique_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(ingest_pdf_file, file_path)
        
    return {
        "message": "File uploaded successfully.",
        "filename": unique_name,
        "path": str(file_path)
    }

@app.get("/pdf/{doc_id:path}")
def get_pdf(doc_id: str):
    pdf_path = get_pdf_path_by_doc_id(doc_id)

    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found.")

    return FileResponse(pdf_path, media_type="application/pdf")