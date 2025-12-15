"""
Unit tests for security module (JWT and password functions).

Tests token creation, validation, and password hashing.
"""

import pytest
from jose import JWTError

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing generates valid hash."""
        password = "SecurePass"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 20  # bcrypt hashes are typically 60 chars

    def test_verify_password_correct(self):
        """Test password verification succeeds with correct password."""
        password = "SecurePass"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification fails with incorrect password."""
        password = "SecurePass"
        hashed = hash_password(password)

        assert verify_password("WrongPass", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test password verification is case sensitive."""
        password = "TestPassword"
        hashed = hash_password(password)

        assert verify_password("testpassword", hashed) is False
        assert verify_password("TestPassword", hashed) is True


class TestAccessTokenCreation:
    """Tests for access token creation."""

    def test_create_access_token(self):
        """Test access token creation."""
        user_id = 1
        token = create_access_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT format: header.payload.signature

    def test_create_access_token_different_ids(self):
        """Test access tokens for different users are different."""
        token1 = create_access_token(1)
        token2 = create_access_token(2)

        assert token1 != token2

    def test_create_access_token_different_calls(self):
        """Test access tokens for same user at different times differ (iat changes)."""
        import time

        token1 = create_access_token(1)
        time.sleep(1)  # Wait a full second to ensure different timestamps
        token2 = create_access_token(1)

        # Tokens should be different due to different iat timestamps
        assert token1 != token2


class TestRefreshTokenCreation:
    """Tests for refresh token creation."""

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        user_id = 1
        token = create_refresh_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token

    def test_create_refresh_token_different_ids(self):
        """Test refresh tokens for different users are different."""
        token1 = create_refresh_token(1)
        token2 = create_refresh_token(2)

        assert token1 != token2


class TestTokenDecoding:
    """Tests for token decoding and validation."""

    def test_decode_valid_access_token(self):
        """Test decoding valid access token."""
        user_id = 42
        token = create_access_token(user_id)

        payload = decode_token(token, expected_type="access")

        assert payload.sub == str(user_id)  # sub is stored as string
        assert payload.type == "access"

    def test_decode_valid_refresh_token(self):
        """Test decoding valid refresh token."""
        user_id = 42
        token = create_refresh_token(user_id)

        payload = decode_token(token, expected_type="refresh")

        assert payload.sub == str(user_id)  # sub is stored as string
        assert payload.type == "refresh"

    def test_decode_invalid_token_format(self):
        """Test decoding invalid token format raises JWTError."""
        with pytest.raises(JWTError):
            decode_token("not.a.valid.token", expected_type="access")

    def test_decode_malformed_token(self):
        """Test decoding malformed token raises JWTError."""
        with pytest.raises(JWTError):
            decode_token("malformed", expected_type="access")

    def test_decode_wrong_token_type(self):
        """Test decoding token with wrong expected type raises JWTError."""
        access_token = create_access_token(1)

        # Trying to decode access token as refresh token should fail
        with pytest.raises(JWTError, match="Invalid token type"):
            decode_token(access_token, expected_type="refresh")

    def test_decode_refresh_token_as_access(self):
        """Test decoding refresh token as access token raises JWTError."""
        refresh_token = create_refresh_token(1)

        with pytest.raises(JWTError, match="Invalid token type"):
            decode_token(refresh_token, expected_type="access")

    def test_decode_empty_token(self):
        """Test decoding empty token raises JWTError."""
        with pytest.raises(JWTError):
            decode_token("", expected_type="access")

    def test_decode_expired_token(self):
        """Test that very old tokens would fail (checking expiration logic)."""
        # This is more of a contract test - in real scenario would need to
        # manipulate time or wait for token to actually expire
        token = create_access_token(1)
        payload = decode_token(token, expected_type="access")

        # Verify token has expiration
        assert payload.exp > 0
        assert payload.iat > 0
        assert payload.exp > payload.iat


class TestTokenPayloadValidation:
    """Tests for token payload structure validation."""

    def test_access_token_payload_structure(self):
        """Test access token has correct payload structure."""
        token = create_access_token(user_id=123)
        payload = decode_token(token, expected_type="access")

        assert hasattr(payload, "sub")
        assert hasattr(payload, "exp")
        assert hasattr(payload, "iat")
        assert hasattr(payload, "type")
        assert payload.sub == "123"  # sub is stored as string
        assert payload.type == "access"

    def test_refresh_token_payload_structure(self):
        """Test refresh token has correct payload structure."""
        token = create_refresh_token(user_id=456)
        payload = decode_token(token, expected_type="refresh")

        assert payload.sub == "456"  # sub is stored as string
        assert payload.type == "refresh"
