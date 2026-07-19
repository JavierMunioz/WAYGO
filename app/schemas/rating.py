from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema
from app.schemas.user import UserMiniResponse


class CreateRatingRequest(BaseSchema):
    score: int = Field(ge=1, le=5)
    review: str | None = Field(None, max_length=1000)


class RatingResponse(BaseSchema):
    id: str
    place_id: str
    score: int
    review: str | None = None
    created_at: datetime
    updated_at: datetime
    user: UserMiniResponse
