from app.repositories.badge_repository import BadgeRepository, BadgeRequirementRepository, UserBadgeRepository
from app.repositories.collection_repository import CollectionRepository, UserCollectionProgressRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.follow_repository import FollowRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.photo_repository import PhotoLikeRepository, PhotoRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.repositories.visit_repository import VisitRepository

__all__ = [
    "UserRepository",
    "RefreshTokenRepository",
    "PlaceRepository",
    "VisitRepository",
    "PhotoRepository",
    "PhotoLikeRepository",
    "FollowRepository",
    "CommentRepository",
    "BadgeRepository",
    "BadgeRequirementRepository",
    "UserBadgeRepository",
    "CollectionRepository",
    "UserCollectionProgressRepository",
    "NotificationRepository",
    "StatsRepository",
]
