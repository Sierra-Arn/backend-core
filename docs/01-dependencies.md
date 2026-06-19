# I. Dependencies Overview

> *This document describes the runtime dependencies required by the Backend Core project.*

## System Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| Pixi | [prefix-dev/pixi](https://github.com/prefix-dev/pixi) | Package and environment manager | 1. Resolves and installs both conda and PyPI dependencies. <br>2. Manages the project's virtual environment and lockfile. |
| Docker | [moby/moby](https://github.com/moby/moby) | Containerization platform | Provides the container runtime that isolates and runs the PostgreSQL and Redis images. |
| Docker Compose | [docker/compose](https://github.com/docker/compose) | Multi-container orchestration tool | Declares containers, their networking, and startup order in a single docker-compose.yml file. |

## Pixi Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| CPython | [python/cpython](https://github.com/python/cpython) | Python virtual machine | Executes all source code across every package. |
| FastAPI | [fastapi/fastapi](https://github.com/fastapi/fastapi) | Async web framework | Provides HTTP routing, request validation, dependency injection, and automatic OpenAPI documentation. |
| Uvicorn | [encode/uvicorn](https://github.com/encode/uvicorn) | ASGI server | Serves the FastAPI application over HTTP. |
| Pydantic Settings | [pydantic/pydantic-settings](https://github.com/pydantic/pydantic-settings) | Settings management library | Loads and validates environment variables for all configuration classes across every package. |
| python-json-logger | [nhairs/python-json-logger](https://github.com/nhairs/python-json-logger) | JSON log formatter | Formats all log records as structured JSON, enabling consistent machine-readable output across every package. |
| SQLAlchemy | [sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) | ORM and database toolkit | Maps Python classes to PostgreSQL tables and manages sessions for all database interactions. |
| Alembic | [sqlalchemy/alembic](https://github.com/sqlalchemy/alembic) | Database migration tool | Manages versioned schema changes and seed data via sequential migration scripts. |
| asyncpg | [MagicStack/asyncpg](https://github.com/MagicStack/asyncpg) | Async PostgreSQL driver | Handles all database connections at runtime via SQLAlchemy's async engine. |
| psycopg2-binary | [psycopg/psycopg2](https://github.com/psycopg/psycopg2) | Sync PostgreSQL driver | Used exclusively by Alembic during migration execution, which runs in a synchronous context. |
| redis-py | [redis/redis-py](https://github.com/redis/redis-py) | Official Redis client | Manages refresh token storage, JWT blacklisting, and sliding window rate limiting. |
| bcrypt | [pyca/bcrypt](https://github.com/pyca/bcrypt) | Password hashing library | Hashes passwords at registration and verifies them at login using the bcrypt algorithm. |
| PyJWT | [jpadilla/pyjwt](https://github.com/jpadilla/pyjwt) | JWT library | Issues, signs, and validates JWT access tokens throughout the authentication flow. |
| just | [casey/just](https://github.com/casey/just) | Command runner [^1] | Provides shorthand recipes for bootstrap commands, migration targets, process launchers, and Docker Compose shortcuts. |

[^1]: Despite using `pixi`, loading environment variables from `.env` files in `pixi tasks` is not straightforward — it requires either `direnv`, custom activation scripts, or declaring all variables directly in `pixi.toml`. Since storing configuration in `.env` files is standard practice, hardcoding variables into `pixi.toml` is not an option for this project. That leaves activation scripts or `direnv` — both of which require extra setup and add implicit behavior. Since you end up adding complexity either way, it makes more sense to pick something transparent — `just` loads `.env` files natively, requires no additional scripts or configuration, and its recipes are plain, readable shell commands with no hidden activation logic.

## Docker Images

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| PostgreSQL | [docker.io/library/postgres](https://hub.docker.com/_/postgres) | Official Docker image for PostgreSQL | Runs the relational database engine in a container, storing all persistent application data: users, roles, permissions, and their associations. |
| Redis | [docker.io/library/redis](https://hub.docker.com/_/redis) | Official Docker image for Redis | Runs the in-memory data store in a container, storing refresh tokens, blacklisted JWT identifiers, and sliding window rate limit counters. |