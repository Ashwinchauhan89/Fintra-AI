"""
Authentication and Security Subsystem for Fintra-AI Backend.

Provides:
1. Clerk JWT Session Token Verification & RBAC Dependency Injection.
2. Inter-Service API Key Authentication (Next.js server actions, ETL pipelines, CLI).
3. Token-Bucket Rate Limiter with Arcjet parity and HTTP 429 response headers.
4. Composite identity resolution (JWT or API Key).
"""

import base64
import json
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

import jwt
from fastapi import Depends, HTTPException, Request, Response, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery, HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Security Scheme Extractors
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query_scheme = APIKeyQuery(name="api_key", auto_error=False)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class AuthenticatedUser:
    """Represents a validated end-user authenticated via Clerk JWT."""

    user_id: str
    email: Optional[str] = None
    session_id: Optional[str] = None
    role: str = "user"
    claims: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        return bool(self.user_id)


@dataclass
class ClientIdentity:
    """Encapsulates the authenticated caller identity (User or Service)."""

    auth_type: str  # "clerk_jwt", "api_key", or "anonymous"
    user: Optional[AuthenticatedUser] = None
    api_key_identifier: Optional[str] = None

    @property
    def identifier(self) -> str:
        """Returns a canonical identifier for logging, auditing, and rate limiting."""
        if self.user:
            return f"user:{self.user.user_id}"
        if self.api_key_identifier:
            return f"service:{self.api_key_identifier}"
        return "anonymous"


# ---------------------------------------------------------------------------
# Rate Limiting Engine (Arcjet Parity & In-Memory Token Bucket)
# ---------------------------------------------------------------------------


class RateLimitExceeded(HTTPException):
    """Custom exception raised when rate limit capacity is exceeded."""

    def __init__(self, limit: int, remaining: int, reset_seconds: int, message: str = "Too many requests"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": message,
                "limit": limit,
                "remaining": remaining,
                "reset_in_seconds": reset_seconds,
            },
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_seconds),
                "Retry-After": str(reset_seconds),
            },
        )


class TokenBucketRateLimiter:
    """
    Thread-safe in-memory Token Bucket rate limiter.
    Provides Arcjet parity with sliding refills and configurable characteristics.
    """

    def __init__(self):
        self._buckets: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._last_cleanup = time.time()

    def _cleanup_stale(self, now: float):
        """Periodically purge entries inactive for more than 1 hour."""
        if now - self._last_cleanup > 3600:
            stale_keys = [k for k, v in self._buckets.items() if now - v.get("last_updated", 0) > 3600]
            for k in stale_keys:
                self._buckets.pop(k, None)
            self._last_cleanup = now

    def check(
        self,
        key: str,
        capacity: int,
        refill_rate: int,
        interval_seconds: int,
        cost: int = 1,
    ) -> Tuple[bool, int, int]:
        """
        Evaluate if a request with `cost` tokens is allowed.
        Returns: (allowed: bool, remaining_tokens: int, reset_seconds: int)
        """
        if not settings.RATE_LIMIT_ENABLED:
            return True, capacity, 0

        now = time.time()
        with self._lock:
            self._cleanup_stale(now)

            bucket = self._buckets.get(key)
            if not bucket:
                bucket = {
                    "tokens": float(capacity),
                    "last_updated": now,
                    "window_start": now,
                }
                self._buckets[key] = bucket

            # Calculate token refill based on elapsed time
            elapsed = now - bucket["last_updated"]
            refill_tokens = elapsed * (refill_rate / float(interval_seconds))
            bucket["tokens"] = min(float(capacity), bucket["tokens"] + refill_tokens)
            bucket["last_updated"] = now

            # Determine reset time (time to full capacity)
            missing_tokens = max(0.0, float(capacity) - bucket["tokens"])
            reset_seconds = int(missing_tokens / (refill_rate / float(interval_seconds))) if refill_rate > 0 else interval_seconds

            if bucket["tokens"] >= cost:
                bucket["tokens"] -= cost
                remaining = int(bucket["tokens"])
                return True, remaining, max(1, reset_seconds)
            else:
                remaining = int(bucket["tokens"])
                return False, remaining, max(1, reset_seconds)

    def reset(self, key: Optional[str] = None):
        """Reset one or all rate limit buckets (useful for unit tests)."""
        with self._lock:
            if key:
                self._buckets.pop(key, None)
            else:
                self._buckets.clear()


# Global in-memory rate limiter singleton
rate_limiter = TokenBucketRateLimiter()


def rate_limit(
    rate: Optional[int] = None,
    window: Optional[int] = None,
    burst_capacity: Optional[int] = None,
    characteristic: str = "client",
):
    """
    FastAPI dependency for endpoint-level rate limiting.
    Matches Arcjet tokenBucket semantics.
    """

    async def _rate_limit_dependency(
        request: Request,
        response: Response,
    ):
        if not settings.RATE_LIMIT_ENABLED:
            return

        eff_rate = rate if rate is not None else settings.RATE_LIMIT_DEFAULT_RATE
        eff_window = window if window is not None else settings.RATE_LIMIT_DEFAULT_WINDOW
        eff_capacity = burst_capacity if burst_capacity is not None else max(eff_rate, settings.RATE_LIMIT_BURST_CAPACITY)

        # Extract characteristic identifier (user_id / api_key / client IP)
        ip = request.client.host if request.client else "127.0.0.1"
        auth_header = request.headers.get("Authorization", "")
        api_key = request.headers.get("X-API-Key", "")
        path = request.url.path

        if characteristic == "user" and auth_header.startswith("Bearer "):
            client_id = f"user:{auth_header[:30]}:{path}"
        elif api_key:
            client_id = f"apikey:{api_key[:10]}:{path}"
        else:
            client_id = f"ip:{ip}:{path}"

        allowed, remaining, reset_secs = rate_limiter.check(
            key=client_id,
            capacity=eff_capacity,
            refill_rate=eff_rate,
            interval_seconds=eff_window,
            cost=1,
        )

        # Inject standard rate limit response headers
        response.headers["X-RateLimit-Limit"] = str(eff_capacity)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_secs)

        if not allowed:
            raise RateLimitExceeded(
                limit=eff_capacity,
                remaining=remaining,
                reset_seconds=reset_secs,
                message="Rate limit exceeded. Please try again later.",
            )

    return _rate_limit_dependency


# ---------------------------------------------------------------------------
# Clerk JWKS & PEM Public Key Caching
# ---------------------------------------------------------------------------


class ClerkKeyManager:
    """Manages decoding and validation keys for Clerk JWT verification."""

    def __init__(self):
        self._jwks_cache: Dict[str, Any] = {}
        self._cache_timestamp: float = 0.0
        self._cache_ttl_seconds: int = 3600  # 1 hour
        self._lock = Lock()

    def get_public_pem(self) -> Optional[str]:
        """Formats the configured PEM public key with proper RSA headers."""
        raw_key = settings.CLERK_PEM_PUBLIC_KEY
        if not raw_key:
            return None

        key_str = raw_key.strip()
        if not key_str.startswith("-----BEGIN"):
            key_str = f"-----BEGIN PUBLIC KEY-----\n{key_str}\n-----END PUBLIC KEY-----"
        return key_str

    def fetch_jwks(self) -> Dict[str, Any]:
        """Fetches Clerk JWKS public keys from URL or Clerk API with caching."""
        now = time.time()
        with self._lock:
            if self._jwks_cache and (now - self._cache_timestamp < self._cache_ttl_seconds):
                return self._jwks_cache

            jwks_url = settings.CLERK_JWKS_URL
            if not jwks_url and settings.CLERK_ISSUER:
                jwks_url = f"{settings.CLERK_ISSUER.rstrip('/')}/.well-known/jwks.json"

            if not jwks_url:
                jwks_url = "https://api.clerk.com/v1/jwks"

            try:
                import httpx

                headers = {}
                if settings.CLERK_SECRET_KEY:
                    headers["Authorization"] = f"Bearer {settings.CLERK_SECRET_KEY}"

                resp = httpx.get(jwks_url, headers=headers, timeout=5.0)
                if resp.status_code == 200:
                    self._jwks_cache = resp.json()
                    self._cache_timestamp = now
                    return self._jwks_cache
            except Exception as e:
                logger.warning("Failed to fetch Clerk JWKS from %s: %s", jwks_url, e)

            return self._jwks_cache


clerk_key_manager = ClerkKeyManager()


# ---------------------------------------------------------------------------
# Token & API Key Verifiers
# ---------------------------------------------------------------------------


def verify_clerk_jwt(token: str) -> AuthenticatedUser:
    """
    Validates a Clerk JWT session token and returns an AuthenticatedUser.
    Supports PEM public keys, JWKS verification, and dev/test tokens.
    """
    if not token or not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Development & Test Mock Token Support
    if settings.DEBUG:
        if token.startswith("test_user_") or token.startswith("mock_user_"):
            user_id = token.split("?")[0]
            return AuthenticatedUser(
                user_id=user_id,
                email=f"{user_id}@fintra.internal",
                role="user",
                claims={"sub": user_id, "mock": True},
            )

    # 2. Try verifying with PEM Public Key
    pem_key = clerk_key_manager.get_public_pem()
    if pem_key:
        try:
            payload = jwt.decode(
                token,
                pem_key,
                algorithms=["RS256", "RS512", "ES256", "HS256"],
                options={"verify_aud": False},
            )
            return _extract_authenticated_user(payload)
        except jwt.PyJWTError as e:
            logger.debug("PEM token decoding failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 3. Try verifying with Clerk JWKS
    jwks = clerk_key_manager.fetch_jwks()
    if jwks and "keys" in jwks:
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            key_dict = None
            for key in jwks["keys"]:
                if key.get("kid") == kid:
                    key_dict = key
                    break

            if key_dict:
                from jwt.algorithms import RSAAlgorithm

                public_key = RSAAlgorithm.from_jwk(json.dumps(key_dict))
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    options={"verify_aud": False},
                )
                return _extract_authenticated_user(payload)
        except Exception as e:
            logger.debug("JWKS token decoding failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token signature verification failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 4. Fallback for Local Dev or Symmetric Secret
    if settings.CLERK_SECRET_KEY:
        try:
            payload = jwt.decode(
                token,
                settings.CLERK_SECRET_KEY,
                algorithms=["HS256", "HS384", "HS512"],
                options={"verify_aud": False},
            )
            return _extract_authenticated_user(payload)
        except Exception:
            pass

    # 5. When in Debug Mode and no keys are configured, allow non-verified decode for local exploration
    if settings.DEBUG:
        try:
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            logger.warning("DEBUG MODE: Decoded JWT without cryptographic verification!")
            return _extract_authenticated_user(unverified_payload)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Malformed token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to verify token signature: No valid Clerk verification keys configured.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _extract_authenticated_user(payload: Dict[str, Any]) -> AuthenticatedUser:
    """Extracts canonical fields from a verified JWT payload."""
    user_id = payload.get("sub") or payload.get("id") or payload.get("userId")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject ('sub') claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract email if present
    email = payload.get("email")
    if not email and "primary_email_address" in payload:
        email = payload["primary_email_address"]
    elif not email and "email_addresses" in payload and isinstance(payload["email_addresses"], list):
        email = payload["email_addresses"][0]

    # Extract role / metadata
    metadata = payload.get("public_metadata", {}) or payload.get("metadata", {})
    role = metadata.get("role", payload.get("role", "user"))
    session_id = payload.get("sid") or payload.get("session_id")

    return AuthenticatedUser(
        user_id=str(user_id),
        email=str(email) if email else None,
        session_id=str(session_id) if session_id else None,
        role=str(role),
        claims=payload,
    )


def verify_api_key(
    header_key: Optional[str] = Security(api_key_header_scheme),
    query_key: Optional[str] = Security(api_key_query_scheme),
) -> str:
    """
    Validates inter-service API key using constant-time string comparison.
    Accepts key via 'X-API-Key' header or '?api_key=' query param.
    """
    provided_key = header_key or query_key
    if not provided_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key in 'X-API-Key' header or query parameter.",
        )

    valid_keys = [settings.BACKEND_API_KEY] + settings.INTERNAL_API_KEYS
    # Constant-time comparison against all configured keys
    is_valid = any(secrets.compare_digest(provided_key, valid_k) for valid_k in valid_keys if valid_k)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or unauthorized API Key.",
        )

    return provided_key


# ---------------------------------------------------------------------------
# FastAPI Route Dependencies
# ---------------------------------------------------------------------------


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> AuthenticatedUser:
    """
    Strict Dependency: Enforces that the request has a valid Clerk JWT Bearer token.
    Raises 401 Unauthorized if token is missing or invalid.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide 'Authorization: Bearer <token>' header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_clerk_jwt(credentials.credentials)


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> Optional[AuthenticatedUser]:
    """
    Optional Dependency: Returns AuthenticatedUser if a valid token is provided,
    otherwise returns None without raising an error.
    """
    if not credentials or not credentials.credentials:
        return None
    try:
        return verify_clerk_jwt(credentials.credentials)
    except Exception:
        return None


def get_authenticated_identity(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    header_key: Optional[str] = Security(api_key_header_scheme),
    query_key: Optional[str] = Security(api_key_query_scheme),
) -> ClientIdentity:
    """
    Flexible Composite Dependency:
    Accepts either a valid Clerk JWT token (user context) or a valid API Key (service context).
    Ideal for ML prediction endpoints invoked by either the frontend or internal background services.
    """
    # 1. Check for Bearer JWT
    if credentials and credentials.credentials:
        try:
            user = verify_clerk_jwt(credentials.credentials)
            return ClientIdentity(auth_type="clerk_jwt", user=user)
        except HTTPException:
            # Fall through to check API Key if JWT verification fails
            pass

    # 2. Check for API Key
    provided_key = header_key or query_key
    if provided_key:
        valid_keys = [settings.BACKEND_API_KEY] + settings.INTERNAL_API_KEYS
        if any(secrets.compare_digest(provided_key, k) for k in valid_keys if k):
            return ClientIdentity(auth_type="api_key", api_key_identifier=provided_key[:8])

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized. Provide a valid Clerk Bearer token or 'X-API-Key' header.",
        headers={"WWW-Authenticate": "Bearer, ApiKey"},
    )


def require_role(required_role: str):
    """
    Role-Based Access Control (RBAC) Dependency Factory.
    Ensures the authenticated Clerk user possesses the specified role.
    """

    def _role_checker(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if user.role != required_role and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires '{required_role}' role.",
            )
        return user

    return _role_checker
