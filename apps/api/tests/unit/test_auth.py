"""Tests for the core authentication module (api/auth.py).

Covers password hashing, JWT token creation/validation, and the
get_current_user dependency used to protect authenticated endpoints.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from api.auth import (
    JWT_ALGORITHM,
    JWT_SECRET,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for bcrypt password hashing and verification."""

    def test_hash_password_creates_valid_hash(self):
        """hash_password should return a bcrypt hash that starts with $2b$."""
        hashed = hash_password("my_password")
        assert hashed.startswith("$2b$")
        assert len(hashed) > 20

    def test_verify_password_correct(self):
        """verify_password should return True for matching password and hash."""
        password = "secure_password_123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_wrong(self):
        """verify_password should return False for non-matching password."""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes_for_same_password(self):
        """hash_password should produce different hashes (salted) for the same input."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        # Both should still verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Tests for JWT access token creation."""

    def test_create_access_token_returns_string(self):
        """create_access_token should return a non-empty string."""
        token = create_access_token("user-id-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_correct_sub_claim(self):
        """The JWT payload should contain the user_id as the 'sub' claim."""
        user_id = "abc-def-123"
        token = create_access_token(user_id)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == user_id

    def test_token_contains_exp_claim(self):
        """The JWT payload should contain an 'exp' (expiration) claim."""
        token = create_access_token("user-id-123")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert "exp" in payload

    def test_token_expiration_is_in_the_future(self):
        """The token's expiration should be set in the future (approx 24h)."""
        token = create_access_token("user-id-123")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        # Should expire roughly 24 hours from now (allow some margin)
        assert exp > now
        assert exp < now + timedelta(hours=25)


class TestGetCurrentUser:
    """Tests for the get_current_user dependency that validates JWT tokens."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self, mock_db, mock_user):
        """A valid JWT token should return the corresponding user from the database."""
        token = create_access_token(mock_user.id)
        credentials = MagicMock()
        credentials.credentials = token

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = await get_current_user(credentials=credentials, db=mock_db)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self, mock_db):
        """An invalid JWT token should raise HTTP 401 Unauthorized."""
        credentials = MagicMock()
        credentials.credentials = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=mock_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self, mock_db):
        """An expired JWT token should raise HTTP 401 Unauthorized."""
        # Create a token that is already expired
        expired_payload = {
            "sub": "user-123",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        credentials = MagicMock()
        credentials.credentials = expired_token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=mock_db)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_nonexistent_user_raises_401(self, mock_db):
        """A valid token for a non-existent user should raise HTTP 401 Unauthorized."""
        token = create_access_token("nonexistent-user-id")
        credentials = MagicMock()
        credentials.credentials = token

        # Database returns None for the user
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=mock_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User not found"

    @pytest.mark.asyncio
    async def test_token_without_sub_raises_401(self, mock_db):
        """A JWT token without a 'sub' claim should raise HTTP 401 Unauthorized."""
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=mock_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"
