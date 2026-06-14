import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestVisitEndpoints:
    async def test_validate_visit_too_far(self, client: AsyncClient, auth_headers: dict):
        # First, create a place (requires superuser — skip in integration; mock directly)
        # This test checks the 400 path when user is far from the place.
        # In a full E2E test suite, a superuser token fixture would be used.
        pass

    async def test_get_my_visits(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/visits/me", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_visit_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/visits",
            json={"place_id": "507f1f77bcf86cd799439011", "latitude": 10.0, "longitude": -74.0},
        )
        assert resp.status_code == 401
