import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "alice", "email": "alice@waygo.test", "password": "Secure123!"},
        )
        assert resp.status_code == 201
        assert "Registration successful" in resp.json()["message"]

    async def test_register_duplicate_email(self, client: AsyncClient):
        payload = {"username": "bob1", "email": "bob@waygo.test", "password": "Secure123!"}
        await client.post("/api/v1/auth/register", json=payload)
        payload["username"] = "bob2"
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409

    async def test_register_duplicate_username(self, client: AsyncClient):
        payload = {"username": "charlie", "email": "charlie1@waygo.test", "password": "Secure123!"}
        await client.post("/api/v1/auth/register", json=payload)
        payload["email"] = "charlie2@waygo.test"
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409

    async def test_login_success(self, client: AsyncClient, registered_user: dict):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": registered_user["password"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, registered_user: dict):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": "WrongPass!"},
        )
        assert resp.status_code == 401

    async def test_refresh_token(self, client: AsyncClient, registered_user: dict):
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": registered_user["refresh_token"]},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_logout(self, client: AsyncClient, registered_user: dict, auth_headers: dict):
        resp = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": registered_user["refresh_token"]},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    async def test_get_me_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 401

    async def test_get_me_with_auth(self, client: AsyncClient, registered_user: dict, auth_headers: dict):
        resp = await client.get("/api/v1/users/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == registered_user["username"]
