import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_KEY=os.getenv("OPENAI_API_KEY")
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHUNK_CHAR_SIZE = int(os.getenv("CHUNK_CHAR_SIZE", "1024"))
CHUNK_CHAR_OVERLAP = int(os.getenv("CHUNK_CHAR_OVERLAP", "200"))
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
PUBLIC_BASE_URL = "http://127.0.0.1:8000"

