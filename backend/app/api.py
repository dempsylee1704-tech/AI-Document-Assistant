from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import RAW_DIR
from io_utils import list_processed_documents
from pydantic import BaseModel
from answer import ask_documents

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
def upload_file(file: UploadFile = File()):
    if not file.filename.lower().endswith(".pdf"):
        HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_path = RAW_DIR / file.filename

    with open(file_path, "wb") as f:
        f.write(file.file.read())
        
    return {
        "message": "File uploaded successfully.",
        "filename": file.filename,
        "path": str(file_path)
    }