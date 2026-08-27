"""Authentication dependency for the government API."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import httpx
import jwt
from fastapi import Depends, Header, HTTPException, status

from .config import get_settings


@dataclass(frozen=True)
class ApiIdentity:
    subject: str
    tenant_id: str
    roles: frozenset[str]


def _jwks_url() -> str:
    settings = get_settings()
    if settings.keycloak_jwks_url:
        return str(settings.keycloak_jwks_url)
    return f"{str(settings.keycloak_issuer).rstrip('/')}/protocol/openid-connect/certs"


@lru_cache(maxsize=1)
def _jwks_client() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(_jwks_url())


def _identity_from_claims(claims: dict[str, Any]) -> ApiIdentity:
    subject = claims.get("sub")
    tenant_id = claims.get("tenant_id") or claims.get("tenant")
    roles_claim = claims.get("roles", ())
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_subject")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="missing_tenant_claim")
    if isinstance(roles_claim, str):
        roles = frozenset(role.strip() for role in roles_claim.split() if role.strip())
    elif isinstance(roles_claim, list):
        roles = frozenset(role for role in roles_claim if isinstance(role, str))
    else:
        roles = frozenset()
    return ApiIdentity(subject=subject, tenant_id=tenant_id, roles=roles)


def _header_text(value: object) -> str | None:
    """Normalize an HTTP header value, including direct dependency calls."""
    return value if isinstance(value, str) else None


async def authenticate(
    authorization: str | None = None,
    x_dev_tenant_id: str | None = None,
    x_dev_subject: str | None = None,
    x_dev_roles: str | None = None,
) -> ApiIdentity:
    """Authenticate normalized header values."""
    settings = get_settings()
    if settings.allow_insecure_dev_auth:
        if not x_dev_tenant_id or not x_dev_subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="development_identity_required"
            )
        roles = frozenset(role.strip() for role in (x_dev_roles or "").split(",") if role.strip())
        return ApiIdentity(x_dev_subject, x_dev_tenant_id, roles)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bearer_token_required")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bearer_token_required")
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256", "RS384", "RS512"],
            audience=settings.keycloak_audience,
            issuer=str(settings.keycloak_issuer),
            options={"require": ["exp", "iat", "sub"]},
        )
    except (jwt.PyJWKError, jwt.PyJWTError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token") from exc
    return _identity_from_claims(claims)


async def require_identity(
    authorization: str | None = Header(default=None),
    x_dev_tenant_id: str | None = Header(default=None),
    x_dev_subject: str | None = Header(default=None),
    x_dev_roles: str | None = Header(default=None),
) -> ApiIdentity:
    return await authenticate(
        _header_text(authorization),
        _header_text(x_dev_tenant_id),
        _header_text(x_dev_subject),
        _header_text(x_dev_roles),
    )


def require_role(*allowed: str):
    async def dependency(identity: ApiIdentity = Depends(require_identity)) -> ApiIdentity:
        if not identity.roles.intersection(allowed):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient_role")
        return identity

    return dependency
