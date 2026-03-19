import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_KEY=os.getenv("OPENAI_API_KEY")
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
CHUNK_CHAR_SIZE = int(os.getenv("CHUNK_CHAR_SIZE", "1200"))
CHUNK_CHAR_OVERLAP = int(os.getenv("CHUNK_CHAR_OVERLAP", "200"))
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

