from datetime import datetime

from pydantic import Field, field_validator

from app.core.constants import PlaceCategory
from app.schemas.common import BaseSchema


class GeoPointSchema(BaseSchema):
    type: str = "Point"
    coordinates: list[float] = Field(min_length=2, max_length=2)


class PlaceResponse(BaseSchema):
    id: str
    name: str
    slug: str
    description: str
    country: str
    city: str
    category: PlaceCategory
    cover_image: str | None = None
    cover_image_source: str | None = None  # "real" | "stock" | None
    validation_radius: float
    location: GeoPointSchema
    opening_hours: str | None = None
    price_range: str | None = None
    fun_fact: str | None = None
    total_visits: int
    total_photos: int
    total_likes: int
    average_rating: float = 0.0
    rating_count: int = 0


class PlaceDetailResponse(PlaceResponse):
    user_has_visited: bool = False


class NearbyPlaceResponse(PlaceResponse):
    distance_meters: float


class CreatePlaceRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    country: str
    city: str
    category: PlaceCategory
    cover_image: str | None = None
    validation_radius: float = Field(default=30.0, ge=10.0, le=500.0)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)
    opening_hours: str | None = Field(None, max_length=200)
    price_range: str | None = Field(None, max_length=100)
    fun_fact: str | None = Field(None, max_length=1000)


class UpdatePlaceRequest(BaseSchema):
    name: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = Field(None, min_length=10, max_length=2000)
    cover_image: str | None = None
    validation_radius: float | None = Field(None, ge=10.0, le=500.0)
    category: PlaceCategory | None = None
    opening_hours: str | None = Field(None, max_length=200)
    price_range: str | None = Field(None, max_length=100)
    fun_fact: str | None = Field(None, max_length=1000)
