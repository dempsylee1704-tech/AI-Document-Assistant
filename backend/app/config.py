import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

#Hauptordner des Backends:
#backend/app
BASE_DIR = Path(__file__).resolve().parent

#Allgemeiner Datenordner:
#backend/app/data
DATA_DIR = BASE_DIR / "data"

#Hochgelademe Dateien
RAW_DIR = BASE_DIR / "data" / "raw"

#Verarbeitete Dateien
PROCESSED_DIR = BASE_DIR / "data" / "processed"

#Lokale SQLite-Datenbank
DATABASE_PATH = DATA_DIR / "assistant.db"

#Die benötigten Ordner automatisch erstellen
for directory in (DATA_DIR, RAW_DIR, PROCESSED_DIR):
    directory.mkdir(parents=True, exist_ok=True)

#OpenAI
API_KEY=os.getenv("OPENAI_API_KEY")

#Chunk-Einstellungen
CHUNK_CHAR_SIZE = int(os.getenv("CHUNK_CHAR_SIZE", "1024"))
CHUNK_CHAR_OVERLAP = int(os.getenv("CHUNK_CHAR_OVERLAP", "200"))

#Qdrant
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

#Backend-Adresse für PDF Quellen
PUBLIC_BASE_URL = "http://127.0.0.1:8000"

#SQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_PATH.as_posix()}"
)

