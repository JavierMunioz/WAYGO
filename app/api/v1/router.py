from fastapi import APIRouter

from app.api.v1 import auth, badges, collections, comments, feed, notifications, photos, places, rankings, users, visits

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(places.router)
api_router.include_router(visits.router)
api_router.include_router(photos.router)
api_router.include_router(feed.router)
api_router.include_router(comments.router)
api_router.include_router(badges.router)
api_router.include_router(collections.router)
api_router.include_router(rankings.router)
api_router.include_router(notifications.router)
