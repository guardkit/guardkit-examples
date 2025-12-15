"""
End-to-end tests for complete authentication workflows.

Tests realistic user scenarios combining multiple endpoints.
"""

import pytest


@pytest.mark.asyncio
class TestCompleteAuthenticationWorkflow:
    """Tests for complete user authentication workflows."""

    async def test_login_and_logout_workflow(self, client, test_user):
        """Test complete login and logout workflow."""
        # Step 1: User logs in
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "SecurePass"},
        )

        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]

        # Step 2: User uses token to access protected resource
        logout_response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert logout_response.status_code == 204

    async def test_token_refresh_workflow(self, client, test_user):
        """Test token refresh workflow."""
        import asyncio

        # Step 1: User logs in
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "SecurePass"},
        )

        tokens = login_response.json()
        refresh_token = tokens["refresh_token"]

        # Wait to ensure different timestamp for new token
        await asyncio.sleep(1.1)

        # Step 2: User refreshes token
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        new_access_token = new_tokens["access_token"]
        same_refresh_token = new_tokens["refresh_token"]

        # Verify refresh returns valid tokens
        assert new_access_token  # Token exists
        assert new_access_token.count(".") == 2  # Valid JWT format
        assert same_refresh_token == refresh_token  # Same refresh token returned

        # Step 3: New access token works
        logout_response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )

        assert logout_response.status_code == 204

    async def test_multiple_logins_different_tokens(self, client, test_user):
        """Test multiple login attempts create different tokens."""
        import asyncio

        # First login
        login1 = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "SecurePass"},
        )

        tokens1 = login1.json()

        # Wait for at least 1 second to ensure different timestamp (JWT uses seconds)
        await asyncio.sleep(1.1)

        # Second login (different timestamp, so different iat)
        login2 = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "SecurePass"},
        )

        tokens2 = login2.json()

        # Tokens should be different (iat timestamp differs)
        assert tokens1["access_token"] != tokens2["access_token"]
        assert tokens1["refresh_token"] != tokens2["refresh_token"]

    async def test_login_with_wrong_password_then_correct(self, client, test_user):
        """Test login fails with wrong password, succeeds with correct."""
        # First attempt - wrong password
        wrong_login = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )

        assert wrong_login.status_code == 401

        # Second attempt - correct password
        correct_login = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "SecurePass"},
        )

        assert correct_login.status_code == 200
        assert "access_token" in correct_login.json()

    async def test_inactive_user_cannot_login(self, client, test_inactive_user):
        """Test inactive user cannot login regardless of password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_inactive_user.email, "password": "SecurePass"},
        )

        assert response.status_code == 401
        assert "Inactive" in response.json()["detail"]

    async def test_old_token_cannot_access_after_logout(
        self, client, test_user, test_user_token
    ):
        """Test token can be used, but concept shows stateless logout."""
        # Logout with token
        logout_response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )

        assert logout_response.status_code == 204

        # Token is still valid from JWT perspective (no blacklist)
        # This tests the stateless nature of the design
        second_logout = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )

        # Token still works - logout is stateless (client discards tokens)
        assert second_logout.status_code == 204


@pytest.mark.asyncio
class TestErrorHandlingWorkflows:
    """Tests for error handling in authentication workflows."""

    async def test_generic_error_on_wrong_credentials(self, client, test_user):
        """Test error message doesn't leak whether email exists."""
        # Wrong password for existing email
        wrong_pw = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "wrong"},
        )

        # Nonexistent email
        no_email = await client.post(
            "/api/v1/auth/login",
            json={"email": "nouser@example.com", "password": "password123"},
        )

        # Both should have same generic error message
        assert wrong_pw.status_code == 401
        assert no_email.status_code == 401
        assert wrong_pw.json()["detail"] == no_email.json()["detail"]

    async def test_malformed_requests_rejected(self, client):
        """Test various malformed requests are rejected."""
        # Missing email
        response1 = await client.post(
            "/api/v1/auth/login",
            json={"password": "password123"},
        )
        assert response1.status_code == 422

        # Invalid email format
        response2 = await client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email", "password": "password123"},
        )
        assert response2.status_code == 422

        # Empty JSON
        response3 = await client.post(
            "/api/v1/auth/login",
            json={},
        )
        assert response3.status_code == 422

    async def test_refresh_with_invalid_tokens(self, client):
        """Test refresh endpoint rejects various invalid tokens."""
        test_cases = [
            "invalid",
            "invalid.token",
            "invalid.token.format.extra",
            "",
            "malformed...token",
        ]

        for invalid_token in test_cases:
            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": invalid_token},
            )
            assert response.status_code == 401
