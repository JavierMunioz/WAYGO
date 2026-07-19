from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field


class Report(Document):
    """Reporte de contenido — hoy solo fotos, pero target_type/target_id
    deja abierto reportar otras cosas (comentarios, usuarios) sin migrar
    el schema. La revisión de reportes es manual por ahora (no hay panel
    de moderación todavía)."""

    reporter_id: Annotated[str, Indexed()]
    target_type: str  # "photo" por ahora
    target_id: Annotated[str, Indexed()]
    reason: str | None = None
    status: str = "pending"  # pending | reviewed | dismissed

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "reports"
        indexes = [
            [("reporter_id", 1), ("target_type", 1), ("target_id", 1)],
        ]
