# Backend Core

> *This directory holds the full technical documentation for Backend Core. This file serves as its entry point: it gives a high-level overview of the service, then points to the file covering each layer of the system, from the technology stack to the runtime behavior of every API operation.*

## I. Project Overview

Backend Core is a headless JSON REST API that implements a self-contained Identity and Access Management (IAM) service. It handles the full user lifecycle — from registration to session termination — while exposing an administrative surface for managing users, roles, and granular permissions.

| Capability | Description |
|---|---|
| Token-based authentication | Short-lived JWT access tokens carry the user's permissions; opaque refresh tokens are stored in Redis with a fixed TTL and are never rotated, allowing the client to reissue access tokens without re-authenticating until the refresh token naturally expires or is explicitly revoked on logout. |
| Role-based access control | Roles group permissions following the `resource:action` convention; administrative endpoints enforce permission checks before the handler executes. |
| Session revocation | Logout blacklists the current access token's `jti` in Redis for its remaining TTL and deletes the refresh token, ensuring both halves of the session are invalidated immediately. |
| IP-based rate limiting | A sliding-window counter in Redis rejects requests from an IP that exceeds the configured threshold before any route logic runs. |
| Access logging | Every request/response pair is logged with method, path, status code, and latency. |
| Uniform error envelope | Validation errors, expected HTTP exceptions, and unhandled failures all produce the same JSON structure, so clients need only one error-parsing path. |

## II. Documentation Overview

Each file focuses on a specific layer of abstraction, ranging from the technology stack to the runtime behavior of individual endpoints.

- To review the runtime dependencies, infrastructure services, and technology stack, see  
    [01-dependencies.md](01-dependencies.md).

- To understand the repository layout, package boundaries, and codebase organization, see  
    [02-project-structure.md](02-project-structure.md).

- To review the runtime interaction patterns and sequence diagrams for every API operation, see  
    [03-request-flows.md](03-request-flows.md).