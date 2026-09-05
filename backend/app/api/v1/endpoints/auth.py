"""
Authentication & Security Status Endpoints for Fintra-AI Backend.
Enables verification of Clerk JWT tokens, session inspection, and API key testing.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, status

from backend.app.core.security import (
    AuthenticatedUser,
    ClientIdentity,
    get_authenticated_identity,
    get_current_user,
    get_optional_user,
    rate_limit,
    require_role,
    verify_api_key,
)

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])


@router.get(
    "/me",
    summary="Get Current Authenticated User (Clerk JWT)",
    description="Inspects the caller's verified Clerk JWT session claims.",
)
def get_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    _rl=Depends(rate_limit()),
) -> Dict[str, Any]:
    return {
        "status": "authenticated",
        "auth_type": "clerk_jwt",
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
        "session_id": current_user.session_id,
    }


@router.get(
    "/verify-key",
    summary="Verify Inter-Service API Key",
    description="Validates the X-API-Key header for server-to-server or ETL communication.",
)
def check_api_key(
    api_key: str = Depends(verify_api_key),
    _rl=Depends(rate_limit()),
) -> Dict[str, Any]:
    return {
        "status": "valid",
        "auth_type": "api_key",
        "key_prefix": api_key[:6] + "..." if len(api_key) > 6 else "***",
    }


@router.get(
    "/identity",
    summary="Resolve Composite Identity (Clerk JWT or API Key)",
    description="Resolves caller identity whether originating from frontend user session or background service.",
)
def resolve_caller_identity(
    identity: ClientIdentity = Depends(get_authenticated_identity),
    _rl=Depends(rate_limit()),
) -> Dict[str, Any]:
    return {
        "status": "authenticated",
        "auth_type": identity.auth_type,
        "identifier": identity.identifier,
        "user_id": identity.user.user_id if identity.user else None,
        "email": identity.user.email if identity.user else None,
    }


@router.get(
    "/admin-only",
    summary="Admin Role Protected Endpoint",
    description="Demonstrates role-based access control (RBAC) requiring 'admin' role.",
)
def admin_only_endpoint(
    admin_user: AuthenticatedUser = Depends(require_role("admin")),
) -> Dict[str, Any]:
    return {
        "status": "success",
        "message": f"Welcome Admin {admin_user.user_id}",
    }
