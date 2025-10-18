"""Tag model para categorização visual."""
from sqlmodel import SQLModel, Field
from typing import Optional


class Tag(SQLModel, table=True):
    """Tag para categorização de hábitos e tarefas."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, index=True)
    color: str = Field(default="#fbd75b")  # Amarelo padrão (Google Calendar ID 5)
    gcal_color_id: int = Field(default=5)  # Para sync futuro
