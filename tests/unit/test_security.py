import pytest

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        plain = "MySecure@Pass123"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct-horse")
        assert not verify_password("wrong-horse", hashed)

    def test_hashes_are_unique(self):
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2  # different salts


class TestJWT:
    def test_access_token_roundtrip(self):
        user_id = "507f1f77bcf86cd799439011"
        token = create_access_token(user_id)
        payload = decode_access_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "access"

    def test_refresh_token_roundtrip(self):
        user_id = "507f1f77bcf86cd799439011"
        token = create_refresh_token(user_id)
        payload = decode_refresh_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_wrong_type_raises(self):
        access_token = create_access_token("some-id")
        with pytest.raises(InvalidTokenError):
            decode_refresh_token(access_token)

    def test_tampered_token_raises(self):
        token = create_access_token("some-id")
        tampered = token[:-5] + "xxxxx"
        with pytest.raises(InvalidTokenError):
            decode_access_token(tampered)
