from app.models.badge import Badge, BadgeRequirement, UserBadge
from app.models.collection import Collection, UserCollectionProgress
from app.models.comment import Comment
from app.models.destination import Destination
from app.models.flight_booking import FlightBooking
from app.models.follow import Follow
from app.models.hotelbeds_destination import HotelbedsDestination
from app.models.itinerary import Itinerary
from app.models.legal import LegalDocument, UserConsent
from app.models.lodging_booking import LodgingBooking
from app.models.notification import Notification
from app.models.otp_code import OTPCode
from app.models.photo import Photo, PhotoLike, PhotoSave
from app.models.place import Place
from app.models.rating import Rating
from app.models.trip import Trip
from app.models.user import RefreshToken, User
from app.models.user_stats import UserStats
from app.models.visit import Visit

BEANIE_DOCUMENT_MODELS = [
    User,
    RefreshToken,
    Place,
    Destination,
    Trip,
    Itinerary,
    FlightBooking,
    LodgingBooking,
    HotelbedsDestination,
    Visit,
    Photo,
    PhotoLike,
    PhotoSave,
    Follow,
    Comment,
    Badge,
    BadgeRequirement,
    UserBadge,
    Collection,
    UserCollectionProgress,
    Notification,
    UserStats,
    OTPCode,
    LegalDocument,
    UserConsent,
    Rating,
]

__all__ = [
    "User",
    "RefreshToken",
    "Place",
    "Destination",
    "Trip",
    "Itinerary",
    "FlightBooking",
    "LodgingBooking",
    "HotelbedsDestination",
    "Visit",
    "Photo",
    "PhotoLike",
    "PhotoSave",
    "Follow",
    "Comment",
    "Badge",
    "BadgeRequirement",
    "UserBadge",
    "Collection",
    "UserCollectionProgress",
    "Notification",
    "UserStats",
    "OTPCode",
    "LegalDocument",
    "UserConsent",
    "Rating",
    "BEANIE_DOCUMENT_MODELS",
]
