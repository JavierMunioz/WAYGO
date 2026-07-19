from app.schemas.common import BaseSchema


class CitySuggestion(BaseSchema):
    city: str
    country: str
    country_code: str
