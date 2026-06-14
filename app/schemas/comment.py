from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema
from app.schemas.user import UserMiniResponse


class CreateCommentRequest(BaseSchema):
    content: str = Field(min_length=1, max_length=1000)


class UpdateCommentRequest(BaseSchema):
    content: str = Field(min_length=1, max_length=1000)


class CommentResponse(BaseSchema):
    id: str
    photo_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    user: UserMiniResponse
