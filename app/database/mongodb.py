import logging
from typing import TYPE_CHECKING

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, GEOSPHERE, TEXT

from app.core.config import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    from app.models import BEANIE_DOCUMENT_MODELS

    logger.info("Connecting to MongoDB...")
    mongodb.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
        maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=45000,
    )
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]

    await init_beanie(database=mongodb.db, document_models=BEANIE_DOCUMENT_MODELS)
    await _create_indexes()
    logger.info("MongoDB connected and indexes ensured.")


async def close_mongo_connection() -> None:
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed.")


async def _create_indexes() -> None:
    db = mongodb.db
    assert db is not None

    # Users
    await db.users.create_index([("email", ASCENDING)], unique=True)
    await db.users.create_index([("username", ASCENDING)], unique=True)
    await db.users.create_index([("points", DESCENDING)])
    await db.users.create_index([("country", ASCENDING), ("points", DESCENDING)])
    await db.users.create_index([("city", ASCENDING), ("points", DESCENDING)])

    # Places
    await db.places.create_index([("location", GEOSPHERE)])
    await db.places.create_index([("slug", ASCENDING)], unique=True)
    await db.places.create_index([("country", ASCENDING), ("city", ASCENDING)])
    await db.places.create_index([("category", ASCENDING)])
    await db.places.create_index([("name", TEXT), ("description", TEXT)])

    # Destinations
    await db.destinations.create_index([("slug", ASCENDING)], unique=True)
    await db.destinations.create_index([("country", ASCENDING), ("city", ASCENDING)])
    await db.destinations.create_index([("name", TEXT), ("description", TEXT)])

    # Trips
    await db.trips.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await db.trips.create_index([("user_id", ASCENDING), ("status", ASCENDING)])

    # Itineraries
    await db.itineraries.create_index([("trip_id", ASCENDING)], unique=True)
    await db.itineraries.create_index([("user_id", ASCENDING)])

    # Flight bookings
    await db.flight_bookings.create_index([("trip_id", ASCENDING)], unique=True)
    await db.flight_bookings.create_index([("user_id", ASCENDING)])

    # Lodging bookings
    await db.lodging_bookings.create_index([("trip_id", ASCENDING)], unique=True)
    await db.lodging_bookings.create_index([("user_id", ASCENDING)])

    # Visits
    await db.visits.create_index([("user_id", ASCENDING), ("place_id", ASCENDING)])
    await db.visits.create_index([("user_id", ASCENDING), ("verified", ASCENDING)])
    await db.visits.create_index([("place_id", ASCENDING), ("created_at", DESCENDING)])

    # Photos
    await db.photos.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await db.photos.create_index([("place_id", ASCENDING), ("created_at", DESCENDING)])
    await db.photos.create_index([("likes_count", DESCENDING)])
    await db.photos.create_index([("created_at", DESCENDING)])

    # Photo Likes
    await db.photo_likes.create_index([("user_id", ASCENDING), ("photo_id", ASCENDING)], unique=True)
    await db.photo_likes.create_index([("photo_id", ASCENDING)])

    # Photo Saves
    await db.photo_saves.create_index([("user_id", ASCENDING), ("photo_id", ASCENDING)], unique=True)
    await db.photo_saves.create_index([("user_id", ASCENDING)])

    # Follows
    await db.follows.create_index([("follower_id", ASCENDING), ("following_id", ASCENDING)], unique=True)
    await db.follows.create_index([("follower_id", ASCENDING)])
    await db.follows.create_index([("following_id", ASCENDING)])

    # Comments
    await db.comments.create_index([("photo_id", ASCENDING), ("created_at", ASCENDING)])
    await db.comments.create_index([("user_id", ASCENDING)])

    # Badges
    await db.badges.create_index([("slug", ASCENDING)], unique=True)
    await db.badges.create_index([("country", ASCENDING), ("city", ASCENDING)])

    # User Badges
    await db.user_badges.create_index([("user_id", ASCENDING), ("badge_id", ASCENDING)], unique=True)
    await db.user_badges.create_index([("user_id", ASCENDING)])

    # Badge Requirements
    await db.badge_requirements.create_index([("badge_id", ASCENDING)], unique=True)

    # Collections
    await db.collections.create_index([("slug", ASCENDING)], unique=True)

    # User Stats
    await db.user_stats.create_index([("user_id", ASCENDING)], unique=True)
    await db.user_stats.create_index([("points", DESCENDING)])
    await db.user_stats.create_index([("country", ASCENDING), ("points", DESCENDING)])
    await db.user_stats.create_index([("city", ASCENDING), ("points", DESCENDING)])

    # Notifications
    await db.notifications.create_index([("user_id", ASCENDING), ("read", ASCENDING), ("created_at", DESCENDING)])
    await db.notifications.create_index([("created_at", DESCENDING)], expireAfterSeconds=90 * 24 * 3600)

    # Token blacklist (JWT revocation via Redis is preferred, this is fallback)
    await db.refresh_tokens.create_index([("user_id", ASCENDING)])
    await db.refresh_tokens.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)

    # Legal Documents
    await db.legal_documents.create_index([("doc_type", ASCENDING), ("is_active", ASCENDING)])
    await db.legal_documents.create_index([("doc_type", ASCENDING), ("version", ASCENDING)], unique=True)

    # User Consents
    await db.user_consents.create_index([("user_id", ASCENDING)])
    await db.user_consents.create_index(
        [("user_id", ASCENDING), ("doc_type", ASCENDING), ("doc_version", ASCENDING)],
        unique=True,
    )
    await db.user_consents.create_index([("doc_type", ASCENDING), ("doc_version", ASCENDING)])
    await db.user_consents.create_index([("consent_uid", ASCENDING)], unique=True)

    logger.info("All indexes created/verified.")
