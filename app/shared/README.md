# **Shared Infrastructure**

*This README provides a high-level overview of the shared infrastructure layer: what each component is for and why it exists. For implementation details refer to the inline comments within each file.*

## **I. Top-level files**

1. **`base_config.py`**
   Defines the base Pydantic Settings class inherited by all configuration schemas across the application. Centralizes common configuration behavior — such as `.env` file loading and case-insensitive field matching — so that individual configs only need to declare their own prefix and fields.

2. **`schemas.py`**
   Defines shared Pydantic models and field mixins reused across multiple modules. Contains `ErrorResponse` — the uniform error envelope returned by all exception handlers — and a set of field mixins (`EmailMixin`, `PasswordMixin`, `AccessTokenMixin`, `RefreshTokenMixin`) that provide consistent field definitions and descriptions across request and response schemas.

3. **`__init__.py`**
   Package initializer for the shared infrastructure layer.

## **II. Directories**

1. **`auth/`**
   Authentication and authorization utilities: JWT encoding and decoding, password hashing, token generation, and FastAPI dependencies (`get_current_user`, `require_permission`) used to protect routes across all feature modules.

2. **`exception_handlers/`**
   Global exception handlers registered on the FastAPI application. Intercepts ``HTTPException``, ``RequestValidationError``, and unhandled exceptions,
   formatting all error responses into the uniform ``ErrorResponse`` envelope.

3. **`logging/`**
   Logging infrastructure: configuration schema and the `get_logger()` factory that produces named JSON loggers.

4. **`middleware/`**
   Application-level middleware. Contains the IP-based rate limiting middleware that enforces a sliding window request limit on every incoming request using Redis, and the access log middleware that records every request's method, URL, client IP, status code, and response time under a dedicated `"access"` logger. Every access log record carries a `"type": "access"` field in the JSON payload, allowing any log aggregation system to filter and separate access logs from internal application logs without custom parsing rules.

5. **`postgres/`**
   PostgreSQL infrastructure: engine and session factory, ORM models, Alembic migrations, and repositories providing typed data access for all domain entities. Inline comments focus on backend-specific concerns rather than PostgreSQL internals — for a deeper exploration of PostgreSQL configuration and behavior, refer to the dedicated [postgresql-core](https://github.com/Sierra-Arn/postgresql-core) project.

6. **`redis/`**
   Redis infrastructure: async client singleton, token blacklist operations, and rate limiting logic backed by a sorted set sliding window algorithm. Inline comments focus on backend-specific concerns rather than Redis internals — for a deeper exploration of Redis configuration and behavior, refer to the dedicated [redis-core](https://github.com/Sierra-Arn/redis-core) project.