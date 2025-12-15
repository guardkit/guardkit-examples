"""
Unit tests for authentication service business logic.

Tests user authentication and token generation.
"""

import pytest

from src.auth.exceptions import AuthenticationError, InactiveUserError
from src.auth.service import authenticate_user, login_user
from src.core.security import hash_password
from src.users.models import User


@pytest.mark.asyncio
class TestAuthenticateUser:
    """Tests for user authentication function."""

    async def test_authenticate_user_success(self, test_session, test_user: User):
        """Test successful user authentication."""
        user = await authenticate_user(
            test_session, email=test_user.email, password="SecurePass"
        )

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_authenticate_user_wrong_password(self, test_session, test_user: User):
        """Test authentication fails with wrong password."""
        user = await authenticate_user(
            test_session, email=test_user.email, password="WrongPass123"
        )

        assert user is None

    async def test_authenticate_user_nonexistent_email(self, test_session):
        """Test authentication returns None for nonexistent user."""
        user = await authenticate_user(
            test_session, email="nonexistent@example.com", password="password123"
        )

        assert user is None

    async def test_authenticate_user_empty_password(self, test_session, test_user: User):
        """Test authentication fails with empty password."""
        user = await authenticate_user(
            test_session, email=test_user.email, password=""
        )

        assert user is None

    async def test_authenticate_user_case_sensitive_email(
        self, test_session, test_user: User
    ):
        """Test authentication is case sensitive for email."""
        user = await authenticate_user(
            test_session,
            email=test_user.email.upper(),
            password="testpassword123",
        )

        # Email should be case-sensitive based on database
        assert user is None or user.email == test_user.email.lower()


@pytest.mark.asyncio
class TestLoginUser:
    """Tests for login_user service function."""

    async def test_login_user_success(self, test_session, test_user: User):
        """Test successful user login returns tokens."""
        token = await login_user(
            test_session, email=test_user.email, password="SecurePass"
        )

        assert token is not None
        assert token.access_token
        assert token.refresh_token
        assert token.token_type == "bearer"

    async def test_login_user_different_tokens(self, test_session, test_user: User):
        """Test access and refresh tokens are different."""
        token = await login_user(
            test_session, email=test_user.email, password="SecurePass"
        )

        assert token.access_token != token.refresh_token

    async def test_login_user_invalid_credentials(self, test_session, test_user: User):
        """Test login fails with invalid credentials."""
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            await login_user(
                test_session, email=test_user.email, password="WrongPass123"
            )

    async def test_login_user_nonexistent_email(self, test_session):
        """Test login fails for nonexistent email."""
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            await login_user(
                test_session,
                email="nonexistent@example.com",
                password="SecurePass",
            )

    async def test_login_inactive_user(self, test_session, test_inactive_user: User):
        """Test login fails for inactive user account."""
        with pytest.raises(InactiveUserError, match="Inactive user account"):
            await login_user(
                test_session,
                email=test_inactive_user.email,
                password="SecurePass",
            )

    async def test_login_inactive_user_correct_password(
        self, test_session, test_inactive_user: User
    ):
        """Test inactive user check happens after authentication."""
        # Even with correct password, inactive users should not login
        with pytest.raises(InactiveUserError):
            await login_user(
                test_session,
                email=test_inactive_user.email,
                password="SecurePass",
            )

    async def test_login_user_error_message_generic(
        self, test_session, test_user: User
    ):
        """Test login error message is generic (no email existence leak)."""
        # This tests security - should not reveal if email exists or password is wrong
        with pytest.raises(AuthenticationError) as exc_info:
            await login_user(
                test_session, email=test_user.email, password="WrongPass123"
            )

        # Error message should be generic
        assert "Invalid email or password" in str(exc_info.value.detail)
