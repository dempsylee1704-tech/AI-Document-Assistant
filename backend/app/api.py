from fastapi import FastAPI
from io_utils import list_processed_documents
from pydantic import BaseModel
from answer import ask_documents

app = FastAPI()

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
