# **Backend Core**

*An educational project demonstrating how to build a backend server with Python, covering authentication, authorization, rate limiting, access logging and global error handling.*

## Project Structure

```bash
backend-core/
├── app/                   # Main application code
├── docker-compose.yml     # Docker Compose configuration for PostgreSQL and Redis services
├── .env.example           # Example environment variables file
├── justfile               # Project-specific commands using Just
├── pixi.lock              # Locked dependency versions for reproducible environments
└── pixi.toml              # Pixi project configuration: environments, dependencies, and platforms
```

Each directory includes its own `README.md` with detailed information about its contents and usage, and every file (except `docker-compose.yml`) contains comprehensive inline comments to explain the code.

## PostgreSQL and Redis as core infrastructure

PostgreSQL was chosen as the primary database because its relational, table-based storage model and full ACID compliance are a natural fit for the security-sensitive data managed by this project — user accounts, roles, permissions, and authentication tokens all require strong consistency and transactional guarantees that an eventually consistent (BASE) system cannot provide. Beyond technical fit, PostgreSQL is released under the PostgreSQL License — one of the most permissive open-source licenses available — making it suitable for use in any project, commercial or otherwise, without legal restrictions. Redis was chosen for token blacklisting and rate limiting due to its native TTL support and sub-millisecond read/write performance. Both databases were also chosen for their familiarity from previous projects — [postgresql-core](https://github.com/Sierra-Arn/postgresql-core) and [redis-core](https://github.com/Sierra-Arn/redis-core).

Since the primary focus here is on demonstrating backend server patterns, the `docker-compose.yml` file contains a minimal configuration for both databases, omitting the more detailed comments found in the projects' compose files.

## Dependencies Overview

- [FastAPI](https://github.com/fastapi/fastapi) — 
a modern, high-performance Python web framework for building APIs, with automatic OpenAPI documentation generation and native support for asynchronous request handling.

- [Uvicorn](https://github.com/Kludex/uvicorn) — 
a lightning-fast ASGI server implementation used to serve the FastAPI application in both development and production environments.

- [pydantic-settings](https://github.com/pydantic/pydantic-settings) — 
a Pydantic-powered library for managing application configuration and environment variables with strong typing, validation, and seamless `.env` support.

- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) — 
the Python SQL toolkit and Object-Relational Mapper (ORM) used as the foundation for database modeling, querying, and transaction management.

- [Alembic](https://github.com/sqlalchemy/alembic) — 
a lightweight database migration tool for SQLAlchemy, enabling structured, version-controlled evolution of the PostgreSQL schema over time.

- [psycopg2-binary](https://github.com/psycopg/psycopg2) — 
the most popular Python client for PostgreSQL, enabling synchronous database connections and operations. Used here exclusively as a dependency for Alembic migrations.

- [asyncpg](https://github.com/MagicStack/asyncpg) — 
a fast Python client for PostgreSQL, enabling asynchronous database connections and operations. Used here as the primary database driver for all runtime database operations.

- [redis-py](https://github.com/redis/redis-py) — 
the official Python client for Redis, used here for token blacklisting and rate limiting via its asyncio interface.

- [PyJWT](https://github.com/jpadilla/pyjwt) — 
a Python library for encoding and decoding JSON Web Tokens, used here for issuing and validating access tokens.

- [bcrypt](https://github.com/pyca/bcrypt) — 
a password hashing library implementing the bcrypt algorithm, used here for secure storage of user credentials.

- [python-json-logger](https://github.com/nhairs/python-json-logger) — 
a Python logging formatter that serializes log records as JSON, enabling structured logging compatible with any log aggregation infrastructure.

- [just](https://github.com/casey/just) — 
a lightweight, cross-platform command runner that replaces complex shell scripts with clean, readable, and reusable project-specific recipes. [^1]

[^1]: Despite using `pixi`, loading environment variables from `.env` files in `pixi tasks` is not straightforward — it requires either `direnv`, custom activation scripts, or declaring all variables directly in `pixi.toml`. Since storing configuration in `.env` files is standard practice, hardcoding variables into `pixi.toml` is not an option for this project. That leaves activation scripts or `direnv` — both of which require extra setup and add implicit behavior. Since you end up adding complexity either way, it makes more sense to pick something transparent — `just` loads `.env` files natively, requires no additional scripts or configuration, and does exactly what it says on the tin.

## Quick Start

### I. Prerequisites

- [Docker and Docker Compose](https://docs.docker.com/engine/install/).
- [Pixi](https://pixi.sh/latest/) package manager.

> **Platform note**: All development and testing were performed on `linux-64`.  
> If you're using a different platform, you’ll need to:
> 1. Update the `platforms` list in the `pixi.toml` accordingly.
> 2. Ensure that platform-specific scripts are compatible with your operating system or replace them with equivalents.

### II. Initial Setup

1. **Clone the repository**

    ```bash
    git clone git@github.com:Sierra-Arn/backend-core.git
    cd backend-core
    ```

2. **Install dependencies**

    ```bash
    pixi install
    ```

3. **Setup environment configuration**

    ```bash
    pixi run just copy-env
    ```

    Review the generated `.env` file and adjust the values as needed. To generate a cryptographically secure JWT secret key, run:

    ```bash
    pixi run just gen-jwt-key
    ```

    Then paste the output into the `AUTHENTICATION_JWT_SECRET_KEY` field in your `.env` file.

4. **Activate pixi environment**
    
    ```bash
    pixi shell
    ```

5. **Prepare initialization scripts**

    ```bash
    just make-x
    just gen-acl
    ```

6. **Start infrastructure services**

   ```bash
   just containers-up
   ```

6. **Apply PostgreSQL migrations**

   ```bash
   just alembic-upgrade
   ```

7. **Seed the database**
   
   ```bash
   just seed-db
   ```

8. **Start the API server**
   
   ```bash
   just api-up
   ```

### III. Testing

Once the API server is running, you can explore and test all available endpoints via the interactive Swagger UI at `http://{UVICORN_HOST}:{UVICORN_PORT}{API_DOCS_URL}`, where the values are taken from your `.env` file.

### IV. Cleanup

When you finish testing:

1. **Stop the API server**  
   In the terminal where the API server is running, press `Ctrl+C` to shut it down.

2. **Stop infrastructure services**

    ```bash
    just containers-down
    ```

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).