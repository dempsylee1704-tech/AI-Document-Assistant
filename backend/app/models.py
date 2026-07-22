from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

def utc_now() -> datetime:
    """
    Gibt die aktuelle Uhrzeit in UTC zurück
    """

    return datetime.now(timezone.utc)

class Conversation(Base):
    """
    Ein Conversations-Datensatz entspricht einem gespeicherten Chat.
    """

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Neuer Chat"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )