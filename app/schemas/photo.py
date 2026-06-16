from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema
from app.schemas.user import UserMiniResponse


class PhotoResponse(BaseSchema):
    id: str
    user_id: str
    place_id: str
    visit_id: str
    image_url: str
    caption: str | None = None
    likes_count: int
    comments_count: int
    is_liked: bool = False
    created_at: datetime


class UploadPhotoRequest(BaseSchema):
    visit_id: str
    place_id: str
    caption: str | None = Field(None, max_length=500)


class FeedItemResponse(BaseSchema):
    id: str
    image_url: str
    caption: str | None = None
    likes_count: int
    comments_count: int
    created_at: datetime
    user: UserMiniResponse
    place_name: str
    place_city: str
    place_id: str
    user_has_liked: bool = False
    is_saved: bool = False
