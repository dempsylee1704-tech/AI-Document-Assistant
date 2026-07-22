import shutil
from uuid import uuid4
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from config import RAW_DIR
from io_utils import list_processed_documents, get_pdf_path_by_doc_id
from pydantic import BaseModel
from answer import ask_documents
from main import ingest_pdf_file
from typing import  List
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import Conversation
from schemas import ConversationCreate
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks,
    Depends)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Wird beim Start des Backends ausgeführt.
    """

    init_db()

    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    print("ASK QUERY:", request.query)
    print("ASK DOC_ID:", request.doc_id)

    result = ask_documents(request.query, request.doc_id)

    print("ASK RESULT:", result)
    return result

@app.post("/conversations")
def create_conversation(
        request: ConversationCreate,
        db: Session = Depends(get_db)
):
    """
    Erstellt einen neuen Chat und speichert ihn in SQLite.
    """

    cleaned_title = request.title.strip()

    if not cleaned_title:
        cleaned_title = "Neuer Chat"

    conversation = Conversation(
        title=cleaned_title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }

@app.get("/conversations")
def get_conversations(
        db: Session = Depends(get_db)
):
    """ 
    Gibt alle gespeicherten Chats zurück.
    Der zuletzt geänderte Chat erscheint zuerst. 
    """

    statement = select(Conversation).order_by(
        Conversation.updated_at.desc()
    )

    conversations = db.scalars(statement).all()

    return {
        "conversations": [
            {"id": conversation.id,
             "title": conversation.title,
             "created_at": conversation.created_at,
             "updated_at": conversation.updated_at
             }
            for conversation in conversations
        ]
    }

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

@app.post("/upload-multiple")
async def upload_multiple_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    uploaded_files = []
    rejected_files = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            rejected_files.append({
                "filename": file.filename,
                "reason": "Only PDF files are allowed."
            })
            continue

        unique_name = f"{uuid4()}_{file.filename}"
        file_path = RAW_DIR / unique_name

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        background_tasks.add_task(ingest_pdf_file, file_path)

        uploaded_files.append({
            "filename": file.filename,
            "stored_filename": unique_name,
            "status": "processing",
            "path": str(file_path)
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