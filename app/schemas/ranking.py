from app.schemas.common import BaseSchema
from app.schemas.user import UserMiniResponse


class RankingEntryResponse(BaseSchema):
    rank: int
    user: UserMiniResponse
    points: int
    places_visited: int
    badges: int
    collections_completed: int
