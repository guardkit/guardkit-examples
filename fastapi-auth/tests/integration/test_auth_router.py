"""
Integration tests for authentication router endpoints.

Tests login, refresh, and logout endpoints with full request/response cycle.
"""

import pytest


@pytest.mark.asyncio
class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login endpoint."""

    async def test_login_success(self, client, test_user):
        """Test successful login returns tokens."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "SecurePass"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_returns_jwt_tokens(self, client, test_user):
        """Test login returns valid JWT format tokens."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "SecurePass"},
        )

        assert response.status_code == 200
        data = response.json()
        # JWT tokens have format: header.payload.signature (3 parts separated by dots)
        assert data["access_token"].count(".") == 2
        assert data["refresh_token"].count(".") == 2

    async def test_login_invalid_credentials(self, client, test_user):
        """Test login fails with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client):
        """Test login fails for nonexistent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_login_inactive_user(self, client, test_inactive_user):
        """Test login fails for inactive user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_inactive_user.email, "password": "SecurePass"},
        )

        assert response.status_code == 401
        assert "Inactive user account" in response.json()["detail"]

    async def test_login_invalid_email_format(self, client):
        """Test login fails with invalid email format."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email", "password": "password123"},
        )

        assert response.status_code == 422  # Validation error

    async def test_login_missing_email(self, client):
        """Test login fails when email is missing."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"password": "password123"},
        )

        assert response.status_code == 422

    async def test_login_missing_password(self, client, test_user):
        """Test login fails when password is missing."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email},
        )

        assert response.status_code == 422

    async def test_login_empty_json(self, client):
        """Test login fails with empty JSON."""
        response = await client.post(
            "/api/v1/auth/login",
            json={},
        )

        assert response.status_code == 422

    async def test_login_response_schema(self, client, test_user):
        """Test login response has correct schema."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "SecurePass"},
        )

        assert response.status_code == 200
        data = response.json()
        # Verify required fields
        assert set(data.keys()) == {"access_token", "refresh_token", "token_type"}
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert isinstance(data["token_type"], str)


@pytest.mark.asyncio
class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh endpoint."""

    async def test_refresh_success(self, client, test_refresh_token):
        """Test successful token refresh."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": test_refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["refresh_token"] == test_refresh_token
        assert data["token_type"] == "bearer"

    async def test_refresh_returns_new_access_token(self, client, test_refresh_token):
        """Test refresh returns a valid access token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": test_refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        # Verify returned token is valid JWT format
        assert data["access_token"]
        assert data["access_token"].count(".") == 2  # header.payload.signature

    async def test_refresh_invalid_token(self, client):
        """Test refresh fails with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.format"},
        )

        assert response.status_code == 401
        assert "Invalid or expired refresh token" in response.json()["detail"]

    async def test_refresh_with_access_token(self, client, test_user_token):
        """Test refresh fails when given access token instead of refresh token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": test_user_token},
        )

        assert response.status_code == 401
        assert "Invalid or expired refresh token" in response.json()["detail"]

    async def test_refresh_empty_token(self, client):
        """Test refresh fails with empty token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": ""},
        )

        assert response.status_code == 401

    async def test_refresh_missing_token(self, client):
        """Test refresh fails when token is missing."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={},
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout endpoint."""

    async def test_logout_success(self, client, test_user_token):
        """Test successful logout returns 204."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )

        assert response.status_code == 204
        assert response.content == b""

    async def test_logout_without_token(self, client):
        """Test logout fails without authentication token."""
        response = await client.post("/api/v1/auth/logout")

        # OAuth2PasswordBearer returns 401 when no token is provided
        assert response.status_code == 401

    async def test_logout_invalid_token(self, client):
        """Test logout fails with invalid token."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid.token.format"},
        )

        assert response.status_code == 401

    async def test_logout_malformed_auth_header(self, client, test_user_token):
        """Test logout fails with malformed auth header."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"InvalidScheme {test_user_token}"},
        )

        # OAuth2PasswordBearer returns 401 for malformed auth header
        assert response.status_code == 401

    async def test_logout_inactive_user(self, client, test_session, test_inactive_user):
        """Test logout fails for inactive user."""
        from src.core.security import create_access_token

        token = create_access_token(test_inactive_user.id)
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestAuthenticationDependencies:
    """Tests for authentication flow through dependencies."""

    async def test_protected_endpoint_with_valid_token(self, client, test_user_token):
        """Test accessing protected endpoint with valid token."""
        # Use logout as a protected endpoint
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )

        assert response.status_code == 204

    async def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = await client.post("/api/v1/auth/logout")

        # OAuth2PasswordBearer returns 401 for missing token
        assert response.status_code == 401

    async def test_protected_endpoint_expired_token(self, client):
        """Test accessing protected endpoint with expired token."""
        # Create an extremely old token (payload with very old iat/exp)
        from unittest.mock import patch
        from datetime import datetime, timedelta, timezone

        with patch("src.core.security.datetime") as mock_datetime:
            # Set time to a date 30+ days in past
            past_time = datetime.now(timezone.utc) - timedelta(days=40)
            mock_datetime.now.return_value = past_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            from src.core.security import create_access_token

            old_token = create_access_token(1)

        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {old_token}"},
        )

        # Should fail because token is expired
        assert response.status_code == 401
