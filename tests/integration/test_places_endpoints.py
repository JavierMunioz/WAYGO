import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPlacesEndpoints:
    async def test_nearby_requires_coordinates(self, client: AsyncClient):
        resp = await client.get("/api/v1/places/nearby")
        assert resp.status_code == 422  # latitude/longitude required

    async def test_nearby_returns_list(self, client: AsyncClient):
        resp = await client.get("/api/v1/places/nearby?latitude=10.9639&longitude=-74.7964&radius_km=5")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_search_requires_query(self, client: AsyncClient):
        resp = await client.get("/api/v1/places/search?q=a")
        assert resp.status_code == 422  # min_length=2

    async def test_search_returns_list(self, client: AsyncClient):
        resp = await client.get("/api/v1/places/search?q=barranquilla")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_create_place_requires_superuser(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/v1/places",
            json={
                "name": "Test Place",
                "description": "A beautiful test place",
                "country": "Colombia",
                "city": "Barranquilla",
                "category": "park",
                "latitude": 10.9639,
                "longitude": -74.7964,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 403  # not superuser
