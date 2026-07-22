from pydantic import BaseModel, Field
from typing import Literal

class ConversationCreate(BaseModel):
    """
    Beschreibt die Daten, die der Benutzer senden muss,
    um einen neuen Chat zu erstellen.
    """

    title: str = Field(
        default="Neuer Chat",
        min_length=1,
        max_length=255
    )

class MessageCreate(BaseModel):
    """
    Daten, die zum Erstellen einer Nachricht benötigt werden.
    """

    role: Literal["user", "assistant"]

    content: str = Field(
        min_length=1
    )