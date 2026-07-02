# II. Project Structure

> *This document describes the logical organization of the project codebase as a Python monorepo. Each package strictly follows the standard `src/` layout for clean imports, independent versioning, and reproducible builds via Pixi.*

## Repository Layout

```
backend-core/
├── packages/           # Monorepo root containing all independently deployable Python modules
│   │                   # and shared libraries. Each package strictly follows the standard
│   │                   # src/ layout (e.g., packages/server/src/server/) for clean imports.
│   │
│   ├── server/         # FastAPI application handling HTTP routing, request validation,
│   │                   # authentication, authorization, rate limiting, access logging,
│   │                   # and global error handling.
│   │
│   ├── shared/         # Cross-process shared infrastructure. Contains base
│   │                   # configurations and unified client abstractions for
│   │                   # external services.
│   │
│   ├── services/       # Cross-process business logic built on top of shared
│   │                   # infrastructure. Contains self-contained service
│   │                   # modules that implement domain-specific behaviour.
│   │
│   └── scripts/        # Standalone automation scripts for environment bootstrapping,
│                       # infrastructure initialization, and auxiliary utility tasks.
│
├── migrations/         # Alembic migration environment and database schema change scripts.
│
├── postgres/           # PostgreSQL initialization scripts generated from environment
│                       # variables at bootstrap time.
│
├── redis/              # Redis ACL initialization scripts generated from environment
│                       # variables at bootstrap time.
│
├── docker-compose.yml  # Docker Compose stack for running infrastructure services
│                       # (PostgreSQL, Redis) locally.
│
├── .env.example        # Environment variable template. Copied to .env during bootstrapping
│                       # with auto-generated credentials for credential fields.
│
├── pixi.toml           # Pixi environment configuration defining dependency groups.
│
├── pixi.lock           # Fully resolved and reproducible dependency lockfile.
│
└── justfile            # Task runner: bootstrap commands, database migration targets,
                        # runtime process launchers, and Docker Compose shortcuts.
                        # Automatically manages pixi environment context per recipe.
```

Every file contains comprehensive inline comments to explain the code. 

> **Note:**  
Since the primary focus here is on demonstrating backend server patterns rather than database configuration, `docker-compose.yml` uses a minimal setup for both databases — for more detailed PostgreSQL and Redis configurations, see [postgresql-core](https://github.com/Sierra-Arn/postgresql-core) and [redis-core](https://github.com/Sierra-Arn/redis-core).

## Package Overview

### 1. `packages/server/`

The FastAPI application serving as the HTTP boundary of the system. Handles request validation, response serialization, authentication, authorization, rate limiting, access logging, and global error handling.

```
server/
├── pyproject.toml
└── src/server/
    ├── app.py                  # FastAPI application factory and middleware registration.
    ├── config.py               # Environment-based settings (Pydantic BaseSettings).
    ├── dependencies.py         # Shared FastAPI dependencies (session injection, auth guards).
    ├── logger.py               # Structured logging configuration.
    ├── main.py                 # Uvicorn entry point for the ASGI server.
    │
    ├── exception_handlers/                    
    │   ├── http.py             # Handles HTTPException raised by route handlers,
    │   │                       # translating status codes into ErrorResponse bodies.
    │   ├── unhandled.py        # Catches all unhandled exceptions, logs the full
    │   │                       # traceback, and returns a generic 500 response.
    │   └── validation.py       # Handles Pydantic RequestValidationError, returning
    │                           # structured 422 responses with field-level detail.
    ├── middleware/
    │   ├── access_log.py       # Logs every request with method, URL, status, and response time.
    │   └── rate_limit.py       # IP-based sliding window rate limiting via Redis.
    │
    └── modules/                # Route handlers grouped by domain resource.
        │
        ├── health/             # Liveness and readiness health check endpoints.
        │   │
        │   ├── shallow/        # Shallow health check (API process only).
        │   └── deep/           # Deep health check (PostgreSQL and Redis connectivity).
        │
        ├── auth/               # Authentication endpoints.
        │   │
        │   ├── register/       # POST /auth/register.
        │   ├── login/          # POST /auth/login .
        │   ├── logout/         # POST /auth/logout.
        │   └── refresh/        # POST /auth/refresh.
        │
        ├── account/                # Authenticated user self-service endpoints.
        │   │
        │   ├── me/                 # GET /account/me.
        │   ├── change_bio/         # PATCH /account/change-bio.
        │   └── change_password/    # PATCH /account/change-password.
        │
        └── admin/                  # Administrative endpoints restricted by RBAC permissions.
            │
            ├── users/              # User management.
            │   │
            │   ├── get/            # GET /admin/users/ and /admin/users/{id}.
            │   ├── update/         # PATCH /admin/users/{id}.
            │   ├── delete/         # DELETE /admin/users/{id}.
            │   └── manage_roles/   # POST/DELETE /admin/users/{id}/roles.
            │
            └── roles/                      # Role management.
                │
                ├── get/                    # GET /admin/roles/ and /admin/roles/{id}.
                ├── create/                 # POST /admin/roles/.
                ├── delete/                 # DELETE /admin/roles/{id}.
                └── manage_permissions/     # POST/DELETE /admin/roles/{id}/permissions.
```

Route handlers are organized by domain resource under `modules/`, with each resource containing subdirectories per HTTP operation. This makes the API surface navigable by resource and operation rather than by technical artifact type.

The `exception_handlers/` directory translates internal exceptions into generic, decoupled error responses. The `middleware/` directory implements cross-cutting concerns applied to every request before it reaches a route handler.

### 2. `packages/shared/`

Centralizes all infrastructure client code and shared utilities consumed across the system. Implements the concrete clients for PostgreSQL and Redis, base configuration primitives, and shared Pydantic schema mixins.

```
shared/
├── pyproject.toml
└── src/
    ├── base_lib/                   # Foundational utilities shared across all packages.
    │   ├── base_config.py          # Base Pydantic settings class with environment variable loading.
    │   └── logger.py               # Structured JSON logging setup shared across all processes.
    │
    ├── postgres_lib/               # Relational database layer.
    │   ├── config.py               # PostgreSQL connection settings.
    │   ├── session.py              # SQLAlchemy async session factory.
    │   ├── models/                 # ORM models for domain entities.
    │   │   ├── base.py             # Declarative base and shared mixins (id, created_at).
    │   │   ├── types.py            # Custom SQLAlchemy column types.
    │   │   ├── user.py             # User model.
    │   │   ├── role.py             # Role model.
    │   │   ├── role_permission.py  # Role-permission association table.
    │   │   └── user_role.py        # User-role association table.
    │   └── repositories/           # Stateless data access layer following the Repository pattern.
    │       ├── base.py             # Generic BaseRepository with common CRUD classmethods.
    │       ├── user.py             # User-specific queries and persistence operations.
    │       └── role.py             # Role-specific queries and permission assignment operations.
    │
    ├── redis_lib/                  # In-memory store client.
    │   ├── config.py               # Redis connection settings with per-database URL properties.
    │   └── client.py               # Async Redis client instances keyed by logical database.
    │
    └── schemas_lib/                # Shared Pydantic field mixins for request and response schemas.
        ├── error.py                # ErrorResponse schema.
        ├── user.py                 # User field mixins.
        ├── role.py                 # Role field mixins.
        └── token.py                # Access and refresh token field mixins.
```

### 3. `packages/services/`

Centralizes cross-process business logic built on top of shared infrastructure. Each library implements a self-contained domain concern and is consumed by the server.

```
services/
├── pyproject.toml
└── src/
    ├── password_lib/               # Password hashing and verification.
    │   ├── config.py               # Bcrypt cost factor and algorithm settings.
    │   └── service.py              # Hash and verify operations via bcrypt.
    │
    ├── rate_limit_lib/             # IP and account based sliding window rate limiting.
    │   ├── config.py               # Maximum requests and window duration settings.
    │   └── service.py              # Sliding window counter operations against Redis.
    │
    └── tokens_lib/                 # JWT access token and opaque refresh token management.
        ├── config.py               # JWT secret, algorithm, and token lifetime settings.
        └── services/
            ├── access_token.py     # JWT issuance, decoding, and blacklist revocation.
            └── refresh_token.py    # Opaque refresh token generation, persistence, and revocation.
```

### 4. `packages/scripts/`

Standalone automation scripts for environment bootstrapping and developer utilities. Not part of the runtime application but essential for development workflow.

```
scripts/
├── pyproject.toml
└── src/scripts/
    ├── quick_start.py                  # Automated startup script. Bootstraps infrastructure, applies
    │                                   # migrations, launches the server, and opens Swagger UI.
    └── utils/                    
        ├── init_env.py                 # Generates .env file from .env.example with secure credentials.
        ├── generate_postgres_sql.py    # Generates PostgreSQL user creation SQL from env vars.
        ├── generate_redis_acl.py       # Generates Redis ACL rules from env vars.
        └── export_swagger.py           # Exports OpenAPI specification to JSON.
```

The `quick_start.py` script orchestrates infrastructure provisioning, database migration, and process launch in the correct dependency order, eliminating manual setup steps. The `utils/` scripts generate infrastructure initialization artifacts from environment variables, enforcing the principle of least privilege for database users and Redis ACLs.

## Infrastructure Directories

### 5. `migrations/`

Alembic migration environment managing the evolution of the database schema. Contains the configuration file (`alembic.ini`), migration script template, and all versioned migration files including the initial schema and seed data.

```
migrations/
├── versions/
│   ├── d167769d594a_auto_migration.py          # Initial schema: users, roles, role_permissions, user_roles.
│   └── 54db352ab472_seed_roles_and_admin.py    # Seeds default roles, permissions, and admin user.
├── alembic.ini                                 # Alembic configuration file.
├── env.py                                      # Migration execution environment.
└── script.py.mako                              # Migration script template.
```

Migrations are generated via `just db-revision` and applied via `just db-migrate`. This separation ensures that schema changes are version-controlled, reviewable, and applied consistently across environments.

The Alembic environment lives outside `packages/` because it is invoked directly via the `alembic` CLI rather than through Python module conventions, and does not follow package layout rules.

### 6. `postgres/` and `redis/`

Infrastructure initialization artifacts generated by the scripts in `packages/scripts/utils/` from environment variables at bootstrap time.

`postgres/` contains the SQL script that creates the application database user with restricted privileges — SELECT, INSERT, UPDATE, and DELETE on tables only, preventing the application user from dropping tables, schemas, or the database itself.

`redis/` contains the ACL configuration that defines two Redis users: an admin user with unrestricted access for operational tasks, and an application user restricted to only the commands the service actually issues (GET, SET, DEL, EXPIRE, ZADD, and similar), with the default user disabled entirely.