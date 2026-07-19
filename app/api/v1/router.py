from fastapi import APIRouter

from app.api.v1 import auth, badges, collections, comments, destinations, feed, flights, itineraries, legal, notifications, photos, places, rankings, trips, users, visits

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(places.router)
api_router.include_router(destinations.router)
api_router.include_router(trips.router)
api_router.include_router(itineraries.router)
api_router.include_router(flights.router)
api_router.include_router(visits.router)
api_router.include_router(photos.router)
api_router.include_router(feed.router)
api_router.include_router(comments.router)
api_router.include_router(badges.router)
api_router.include_router(collections.router)
api_router.include_router(rankings.router)
api_router.include_router(notifications.router)
api_router.include_router(legal.router)
