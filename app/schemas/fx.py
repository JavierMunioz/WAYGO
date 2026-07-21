from app.schemas.common import BaseSchema


class FxRatesResponse(BaseSchema):
    base: str = "USD"
    rates: dict[str, float]
    updated_at: str | None = None
