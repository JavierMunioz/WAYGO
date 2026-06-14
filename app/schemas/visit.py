from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema
from app.schemas.place import PlaceResponse


class ValidateVisitRequest(BaseSchema):
    place_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class VisitResponse(BaseSchema):
    id: str
    user_id: str
    place_id: str
    latitude: float
    longitude: float
    distance: float
    verified: bool
    created_at: datetime


class VisitWithPlaceResponse(VisitResponse):
    place: PlaceResponse | None = None
