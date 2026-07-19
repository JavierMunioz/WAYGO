from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema


class DestinationResponse(BaseSchema):
    id: str
    name: str
    slug: str
    country: str
    city: str
    description: str
    cover_image: str | None = None
    timezone: str | None = None
    currency: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CreateDestinationRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=200)
    country: str = Field(min_length=2, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=10, max_length=2000)
    cover_image: str | None = None
    timezone: str | None = None
    currency: str | None = None


class UpdateDestinationRequest(BaseSchema):
    name: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = Field(None, min_length=10, max_length=2000)
    cover_image: str | None = None
    timezone: str | None = None
    currency: str | None = None
    is_active: bool | None = None
