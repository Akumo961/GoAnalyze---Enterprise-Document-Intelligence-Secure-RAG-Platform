# Phase 6 — Secure HTTP service integration

## Scope

Phase 6 turns the durable Phase 5 workflow into a service boundary:

- FastAPI application and versioned `/v1/cases` endpoints;
- create, retrieve, queue-list, assignment, and state-transition operations;
- tenant identity is derived from an authenticated identity, never from a request body;
- production authentication validates signed Keycloak OIDC JWTs for issuer, audience, expiry, and subject;
- production API does not enable the explicitly named insecure development header mode;
- role checks protect case creation, assignment, and decision workflow operations;
- HTTP integration tests exercise the ASGI application with the same repository/session boundary used by the service;
- production API documentation endpoints are disabled by configuration in production.

## Evidence gates

The Phase 6 acceptance workflow executes:

1. Phase 6 HTTP integration tests.
2. Full Python test suite.
3. Ruff.
4. mypy.

A green workflow proves only the tested commit. A live Keycloak/PostgreSQL deployment remains an additional environment-specific validation gate.

## Security boundaries

- Development header identity is opt-in and rejected by production configuration validation.
- Production tokens must be signed OIDC JWTs; tenant and subject claims are required.
- API paths do not accept a caller-supplied tenant identifier.
- Repository queries continue to enforce tenant scoping server-side.
- This phase does not claim a completed external penetration test, privacy assessment, or government certification.
