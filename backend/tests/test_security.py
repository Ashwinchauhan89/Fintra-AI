"""
Unit and Integration Tests for Fintra-AI Backend Authentication and Security.
Tests Clerk JWT token verification, API Key authentication, rate limiting, and RBAC.
"""

import time
import unittest
from unittest.mock import patch

import jwt
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.security import (
    AuthenticatedUser,
    ClientIdentity,
    RateLimitExceeded,
    TokenBucketRateLimiter,
    rate_limiter,
    verify_api_key,
    verify_clerk_jwt,
)
from backend.app.main import app


class TestApiKeyAuthentication(unittest.TestCase):
    """Tests inter-service API Key authentication logic."""

    def setUp(self):
        self.valid_key = settings.BACKEND_API_KEY

    def test_valid_api_key_header(self):
        res = verify_api_key(header_key=self.valid_key, query_key=None)
        self.assertEqual(res, self.valid_key)

    def test_valid_api_key_query(self):
        res = verify_api_key(header_key=None, query_key=self.valid_key)
        self.assertEqual(res, self.valid_key)

    def test_missing_api_key(self):
        with self.assertRaises(HTTPException) as ctx:
            verify_api_key(header_key=None, query_key=None)
        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("Missing API Key", ctx.exception.detail)

    def test_invalid_api_key(self):
        with self.assertRaises(HTTPException) as ctx:
            verify_api_key(header_key="wrong_key_12345", query_key=None)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("Invalid", ctx.exception.detail)


class TestClerkJwtVerification(unittest.TestCase):
    """Tests Clerk JWT token verification, subject parsing, and claims handling."""

    def test_dev_mock_token(self):
        with patch.object(settings, "DEBUG", True):
            user = verify_clerk_jwt("test_user_abc123")
            self.assertEqual(user.user_id, "test_user_abc123")
            self.assertEqual(user.email, "test_user_abc123@fintra.internal")
            self.assertEqual(user.role, "user")
            self.assertTrue(user.is_authenticated)

    def test_symmetric_secret_jwt(self):
        secret = "super_secret_test_key_for_signing_jwt_tokens_123"
        payload = {
            "sub": "user_clerk_456",
            "email": "user@example.com",
            "role": "member",
            "sid": "sess_789",
        }
        token = jwt.encode(payload, secret, algorithm="HS256")

        with patch.object(settings, "CLERK_SECRET_KEY", secret), patch.object(settings, "DEBUG", False):
            user = verify_clerk_jwt(token)
            self.assertEqual(user.user_id, "user_clerk_456")
            self.assertEqual(user.email, "user@example.com")
            self.assertEqual(user.role, "member")
            self.assertEqual(user.session_id, "sess_789")

    def test_missing_sub_claim(self):
        secret = "super_secret_test_key_for_missing_sub_test_123"
        payload = {"email": "no_sub@example.com"}
        token = jwt.encode(payload, secret, algorithm="HS256")

        with patch.object(settings, "CLERK_SECRET_KEY", secret), patch.object(settings, "DEBUG", False):
            with self.assertRaises(HTTPException) as ctx:
                verify_clerk_jwt(token)
            self.assertEqual(ctx.exception.status_code, 401)

    def test_rsa_pem_verification(self):
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from backend.app.core.security import clerk_key_manager

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        payload = {"sub": "user_rsa_999", "email": "rsa@fintra.internal", "role": "admin"}
        token = jwt.encode(payload, private_key, algorithm="RS256")

        with patch.object(settings, "CLERK_PEM_PUBLIC_KEY", pem_public), patch.object(settings, "DEBUG", False):
            clerk_key_manager._jwks_cache = {}
            user = verify_clerk_jwt(token)
            self.assertEqual(user.user_id, "user_rsa_999")
            self.assertEqual(user.email, "rsa@fintra.internal")
            self.assertEqual(user.role, "admin")

    def test_expired_token_rejection(self):
        secret = "super_secret_test_key_for_expired_sub_test_123"
        # Token expired in the past
        payload = {"sub": "user_expired", "exp": int(time.time()) - 3600}
        token = jwt.encode(payload, secret, algorithm="HS256")

        with patch.object(settings, "CLERK_SECRET_KEY", secret), patch.object(settings, "DEBUG", False):
            with self.assertRaises(HTTPException) as ctx:
                verify_clerk_jwt(token)
            self.assertEqual(ctx.exception.status_code, 401)


class TestRateLimiter(unittest.TestCase):
    """Tests token bucket rate limiter capacity, exhaustion, and Arcjet parity."""

    def setUp(self):
        self.limiter = TokenBucketRateLimiter()

    def test_token_bucket_consumption(self):
        key = "test_client_ip_1"
        # Capacity of 3 requests, refill rate 1 per 60s
        allowed, remaining, reset_secs = self.limiter.check(
            key=key, capacity=3, refill_rate=1, interval_seconds=60, cost=1
        )
        self.assertTrue(allowed)
        self.assertEqual(remaining, 2)

        allowed, remaining, _ = self.limiter.check(
            key=key, capacity=3, refill_rate=1, interval_seconds=60, cost=1
        )
        self.assertTrue(allowed)
        self.assertEqual(remaining, 1)

        allowed, remaining, _ = self.limiter.check(
            key=key, capacity=3, refill_rate=1, interval_seconds=60, cost=1
        )
        self.assertTrue(allowed)
        self.assertEqual(remaining, 0)

        # 4th request exceeds capacity
        allowed, remaining, reset_secs = self.limiter.check(
            key=key, capacity=3, refill_rate=1, interval_seconds=60, cost=1
        )
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)
        self.assertGreater(reset_secs, 0)

    def test_limiter_reset(self):
        key = "test_reset_key"
        self.limiter.check(key=key, capacity=1, refill_rate=1, interval_seconds=60, cost=1)
        # Verify exhausted
        allowed, _, _ = self.limiter.check(key=key, capacity=1, refill_rate=1, interval_seconds=60, cost=1)
        self.assertFalse(allowed)

        # Reset bucket
        self.limiter.reset(key)
        allowed, remaining, _ = self.limiter.check(key=key, capacity=1, refill_rate=1, interval_seconds=60, cost=1)
        self.assertTrue(allowed)


class TestSecurityEndpointsIntegration(unittest.TestCase):
    """Integration tests on FastAPI endpoints with TestClient."""

    def setUp(self):
        self.client = TestClient(app)
        rate_limiter.reset()

    def test_security_headers_present(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")

    def test_auth_me_unauthorized_without_token(self):
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_auth_me_authorized_with_bearer_token(self):
        with patch.object(settings, "DEBUG", True):
            response = self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer test_user_john_doe"},
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "authenticated")
            self.assertEqual(data["user_id"], "test_user_john_doe")
            self.assertEqual(data["auth_type"], "clerk_jwt")

    def test_verify_key_endpoint_success(self):
        response = self.client.get(
            "/api/v1/auth/verify-key",
            headers={"X-API-Key": settings.BACKEND_API_KEY},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "valid")
        self.assertEqual(data["auth_type"], "api_key")

    def test_verify_key_endpoint_forbidden_on_bad_key(self):
        response = self.client.get(
            "/api/v1/auth/verify-key",
            headers={"X-API-Key": "invalid_random_key_xyz"},
        )
        self.assertEqual(response.status_code, 403)

    def test_composite_identity_resolution(self):
        with patch.object(settings, "DEBUG", True):
            # Via Bearer JWT
            res_jwt = self.client.get(
                "/api/v1/auth/identity",
                headers={"Authorization": "Bearer test_user_sam"},
            )
            self.assertEqual(res_jwt.status_code, 200)
            self.assertEqual(res_jwt.json()["auth_type"], "clerk_jwt")
            self.assertEqual(res_jwt.json()["user_id"], "test_user_sam")

            # Via API Key
            res_api = self.client.get(
                "/api/v1/auth/identity",
                headers={"X-API-Key": settings.BACKEND_API_KEY},
            )
            self.assertEqual(res_api.status_code, 200)
            self.assertEqual(res_api.json()["auth_type"], "api_key")

    def test_rbac_admin_endpoint(self):
        # Regular user should be forbidden (403)
        secret = "jwt_signing_key_secret_for_rbac_test"
        regular_payload = {"sub": "user_reg", "role": "user"}
        admin_payload = {"sub": "admin_boss", "role": "admin"}

        user_token = jwt.encode(regular_payload, secret, algorithm="HS256")
        admin_token = jwt.encode(admin_payload, secret, algorithm="HS256")

        with patch.object(settings, "CLERK_SECRET_KEY", secret), patch.object(settings, "DEBUG", False):
            # Non-admin user
            res_user = self.client.get(
                "/api/v1/auth/admin-only",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            self.assertEqual(res_user.status_code, 403)

            # Admin user
            res_admin = self.client.get(
                "/api/v1/auth/admin-only",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            self.assertEqual(res_admin.status_code, 200)
            self.assertIn("admin_boss", res_admin.json()["message"])

    def test_endpoint_rate_limit_exceeded(self):
        # Simulate exceeding rate limits on /auth/verify-key
        with patch.object(settings, "RATE_LIMIT_DEFAULT_RATE", 2), patch.object(settings, "RATE_LIMIT_BURST_CAPACITY", 2):
            rate_limiter.reset()
            # 1st request -> 200
            res1 = self.client.get("/api/v1/auth/verify-key", headers={"X-API-Key": settings.BACKEND_API_KEY})
            # 2nd request -> 200
            res2 = self.client.get("/api/v1/auth/verify-key", headers={"X-API-Key": settings.BACKEND_API_KEY})
            # 3rd request -> 429
            res3 = self.client.get("/api/v1/auth/verify-key", headers={"X-API-Key": settings.BACKEND_API_KEY})
            self.assertEqual(res3.status_code, 429)
            self.assertEqual(res3.json().get("code"), "RATE_LIMIT_EXCEEDED")
            self.assertIn("X-RateLimit-Reset", res3.headers)


if __name__ == "__main__":
    unittest.main()
