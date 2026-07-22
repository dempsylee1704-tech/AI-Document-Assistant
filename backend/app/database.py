from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,Session,sessionmaker

from config import DATABASE_URL


class Base(DeclarativeBase):
    """
    Basisklasse für unsere Datanbanktabellen.
    """

    pass

#SQLite benötigt diese Einstellungen,
#weil FastAPI mehrere Threads verwenden kann.
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

#Stellt die grundsätzliche Verbindung zur Datenbank her.
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

#Erstellt später einzelne Arbeitssitzungen mit der Datenbank.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

def get_db() -> Generator[Session, None, None]:
    """Öffnet eine Datenbanksitzung für einen API-Aufruf
    und schließt sie anschließend wieder.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Erstellt alle bisher definierten Datenbanktabellen.

    Bereits vorhandene Tabellen werden nicht gelöscht.
    """

    import models

    Base.metadata.create_all(bind=engine)