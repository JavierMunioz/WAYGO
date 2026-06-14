from enum import StrEnum


class PlaceCategory(StrEnum):
    BEACH = "beach"
    MOUNTAIN = "mountain"
    MUSEUM = "museum"
    PARK = "park"
    MONUMENT = "monument"
    RESTAURANT = "restaurant"
    VIEWPOINT = "viewpoint"
    WATERFALL = "waterfall"
    ARCHAEOLOGICAL = "archaeological"
    URBAN = "urban"
    NATURAL = "natural"
    RELIGIOUS = "religious"
    OTHER = "other"


class BadgeLevel(StrEnum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    EXPLORER = "explorer"
    MASTER = "master"
    LEGEND = "legend"


class NotificationType(StrEnum):
    NEW_BADGE = "new_badge"
    COLLECTION_COMPLETED = "collection_completed"
    PHOTO_LIKE = "photo_like"
    NEW_FOLLOWER = "new_follower"
    COMMENT = "comment"
    VISIT_MILESTONE = "visit_milestone"


class FeedMode(StrEnum):
    RECENT = "recent"
    POPULAR = "popular"
    TRENDING = "trending"
    FOLLOWING = "following"


class RankingScope(StrEnum):
    GLOBAL = "global"
    COUNTRY = "country"
    CITY = "city"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"


EARTH_RADIUS_METERS = 6_371_000
MAX_PHOTO_SIZE_MB = 10
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
