from app.core.exceptions import ForbiddenError
from app.models.trip import Trip


def ensure_trip_owner(trip: Trip, user_id: str) -> None:
    if trip.user_id != user_id:
        raise ForbiddenError("You do not own this trip")
