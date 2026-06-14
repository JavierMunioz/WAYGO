import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.models import BEANIE_DOCUMENT_MODELS


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["waygo_test"]
    await init_beanie(database=db, document_models=BEANIE_DOCUMENT_MODELS)
    yield db
    client.drop_database("waygo_test")
    client.close()


@pytest_asyncio.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    payload = {
        "username": "testuser",
        "email": "testuser@waygo.test",
        "password": "Str0ngPass!",
    }
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    data = resp.json()
    return {**payload, "access_token": data["access_token"], "refresh_token": data["refresh_token"]}


@pytest_asyncio.fixture
def auth_headers(registered_user: dict) -> dict:
    return {"Authorization": f"Bearer {registered_user['access_token']}"}
