from pydantic import BaseModel, Field

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