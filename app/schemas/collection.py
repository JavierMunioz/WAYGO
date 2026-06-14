from datetime import datetime

from app.schemas.common import BaseSchema


class CollectionResponse(BaseSchema):
    id: str
    name: str
    slug: str
    description: str
    cover_image: str | None = None
    points: int
    total_places: int


class CollectionProgressResponse(CollectionResponse):
    visited_places: int
    progress_pct: float
    completed: bool
    completed_at: datetime | None = None
