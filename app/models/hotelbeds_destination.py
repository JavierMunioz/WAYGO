from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field


class HotelbedsDestination(Document):
    """Catálogo local de destinos de Hotelbeds — se sincroniza una sola vez
    (y se refresca ocasionalmente) para poder ofrecer autocompletado sin
    pegarle a la API externa en cada tecla que escribe el usuario."""

    code: Annotated[str, Indexed(unique=True)]
    name: str
    country_code: Annotated[str, Indexed()]

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "hotelbeds_destinations"
        indexes = [
            [("name", "text")],
        ]
