from app.models.badge import Badge, BadgeRequirement, UserBadge
from app.models.collection import Collection, UserCollectionProgress
from app.models.comment import Comment
from app.models.follow import Follow
from app.models.notification import Notification
from app.models.otp_code import OTPCode
from app.models.photo import Photo, PhotoLike, PhotoSave
from app.models.place import Place
from app.models.user import RefreshToken, User
from app.models.user_stats import UserStats
from app.models.visit import Visit

BEANIE_DOCUMENT_MODELS = [
    User,
    RefreshToken,
    Place,
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
]

__all__ = [
    "User",
    "RefreshToken",
    "Place",
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
    "BEANIE_DOCUMENT_MODELS",
]
