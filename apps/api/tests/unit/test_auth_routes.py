"""Tests for auth route handlers (api/routes/auth.py).

Covers signup (user creation, duplicate email, validation), login
(valid credentials, wrong password, non-existent email), and get_me.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes.auth import signup, login, get_me, _user_to_response
from api.schemas.auth import SignupRequest, LoginRequest


class TestUserToResponse:
    """Tests for the _user_to_response helper function."""

    def test_converts_user_to_response(self, mock_user):
        """_user_to_response should convert a User model to a UserResponse with parsed skills."""
        response = _user_to_response(mock_user)
        assert response.id == mock_user.id
        assert response.email == mock_user.email
        assert response.full_name == mock_user.full_name
        assert response.skills == ["Python", "FastAPI"]
        assert response.availability_status == "available"

    def test_handles_null_availability(self, mock_user):
        """_user_to_response should default availability_status to 'available' when None."""
        mock_user.availability_status = None
        response = _user_to_response(mock_user)
        assert response.availability_status == "available"

    def test_includes_social_urls(self, mock_user):
        """_user_to_response should include linkedin, github, and portfolio URLs."""
        mock_user.linkedin_url = "https://linkedin.com/in/testuser"
        mock_user.github_url = "https://github.com/testuser"
        mock_user.portfolio_url = "https://testuser.dev"
        response = _user_to_response(mock_user)
        assert response.linkedin_url == "https://linkedin.com/in/testuser"
        assert response.github_url == "https://github.com/testuser"
        assert response.portfolio_url == "https://testuser.dev"


class TestSignup:
    """Tests for the POST /auth/signup endpoint."""

    @pytest.mark.asyncio
    async def test_signup_creates_user(self, mock_db):
        """Signup with valid data should create a user and return a JWT token."""
        # No existing user with this email
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = SignupRequest(
            email="new@email.it",
            password="password123",
            full_name="New User",
        )

        # Mock the db operations (add, commit, refresh)
        def mock_refresh(user):
            user.id = str(uuid4())

        mock_db.refresh.side_effect = mock_refresh

        with patch("api.routes.auth.create_access_token", return_value="fake-jwt-token"):
            result = await signup(data=data, db=mock_db)

        assert result.access_token == "fake-jwt-token"
        assert result.token_type == "bearer"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_signup_duplicate_email_returns_409(self, mock_db, mock_user):
        """Signup with an already registered email should raise HTTP 409 Conflict."""
        # Existing user found
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        data = SignupRequest(
            email="test@email.it",
            password="password123",
            full_name="Duplicate User",
        )

        with pytest.raises(HTTPException) as exc_info:
            await signup(data=data, db=mock_db)
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Email already registered"

    def test_signup_short_password_validation(self):
        """Signup with a password shorter than 6 characters should fail Pydantic validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(
                email="test@email.it",
                password="12345",
                full_name="Short Pass",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("password",) for e in errors)

    def test_signup_invalid_email_validation(self):
        """Signup with an invalid email format should fail Pydantic validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SignupRequest(
                email="not-an-email",
                password="password123",
                full_name="Bad Email",
            )


class TestLogin:
    """Tests for the POST /auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, mock_db, mock_user):
        """Login with correct email and password should return a JWT token."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        data = LoginRequest(email="test@email.it", password="password123")

        with patch("api.routes.auth.verify_password", return_value=True), \
             patch("api.routes.auth.create_access_token", return_value="fake-jwt-token"):
            result = await login(data=data, db=mock_db)

        assert result.access_token == "fake-jwt-token"
        assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, mock_db, mock_user):
        """Login with wrong password should raise HTTP 401 Unauthorized."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        data = LoginRequest(email="test@email.it", password="wrong_password")

        with patch("api.routes.auth.verify_password", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await login(data=data, db=mock_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_login_nonexistent_email(self, mock_db):
        """Login with a non-existent email should raise HTTP 401 Unauthorized."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = LoginRequest(email="unknown@email.it", password="password123")

        with pytest.raises(HTTPException) as exc_info:
            await login(data=data, db=mock_db)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid credentials"


class TestGetMe:
    """Tests for the GET /auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_returns_user_profile(self, mock_user):
        """get_me should return the current user's profile as a UserResponse."""
        result = await get_me(current_user=mock_user)
        assert result.id == mock_user.id
        assert result.email == mock_user.email
        assert result.full_name == mock_user.full_name
        assert result.skills == ["Python", "FastAPI"]

    @pytest.mark.asyncio
    async def test_get_me_returns_company_fields(self, mock_company_user):
        """get_me should include company fields for company users."""
        result = await get_me(current_user=mock_company_user)
        assert result.user_type == "company"
        assert result.company_name == "TechFlow Italia"
        assert result.company_website == "https://techflow.it"
        assert result.company_size == "51-200"
        assert result.industry == "Software & Technology"


class TestCompanySignup:
    """Tests for company-specific signup behavior."""

    @pytest.mark.asyncio
    async def test_company_signup_creates_company_user(self, mock_db):
        """Signup with user_type='company' should create a company user."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = SignupRequest(
            email="company@example.it",
            password="password123",
            full_name="Company Admin",
            user_type="company",
            company_name="Test Corp",
            company_website="https://testcorp.it",
            industry="Technology",
        )

        def mock_refresh(user):
            user.id = str(uuid4())

        mock_db.refresh.side_effect = mock_refresh

        with patch("api.routes.auth.create_access_token", return_value="fake-jwt-token"):
            result = await signup(data=data, db=mock_db)

        assert result.access_token == "fake-jwt-token"
        # Verify the user was created with company fields
        added_user = mock_db.add.call_args[0][0]
        assert added_user.user_type == "company"
        assert added_user.company_name == "Test Corp"
        assert added_user.company_website == "https://testcorp.it"
        assert added_user.industry == "Technology"

    def test_company_signup_requires_company_name(self):
        """Signup with user_type='company' but no company_name should fail validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(
                email="company@example.it",
                password="password123",
                full_name="Company Admin",
                user_type="company",
                # missing company_name
            )
        errors = exc_info.value.errors()
        assert any("company_name" in str(e) for e in errors)

    def test_talent_signup_does_not_require_company_name(self):
        """Signup with user_type='talent' should not require company_name."""
        data = SignupRequest(
            email="talent@example.it",
            password="password123",
            full_name="Talent User",
            user_type="talent",
        )
        assert data.user_type == "talent"
        assert data.company_name is None

    def test_signup_invalid_user_type(self):
        """Signup with invalid user_type should fail validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SignupRequest(
                email="test@example.it",
                password="password123",
                full_name="Test User",
                user_type="admin",
            )
