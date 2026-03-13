# **Feature Modules**

*This README provides a high-level overview of the feature modules layer: what each module is responsible for and why it exists. For implementation details refer to the inline comments within each file.*

## **I. `__init__.py`**

Aggregates all feature routers (`auth`, `account`, `users`, `roles`, `health`) into a single import point, which is then registered on the FastAPI application in `app/__init__.py`.

## **II. Modules**

1. **`auth/`**
   Handles all authentication flows: registration, login, logout, and token rotation. Issues and invalidates JWT access/refresh token pairs.

2. **`account/`**
   Manages authenticated user's own account: updating biographical information and changing the password. All endpoints require a valid access token.

3. **`users/`**
   Administrative operations over user accounts: retrieving the full user list and managing role assignments. All endpoints require appropriate permissions.

4. **`roles/`**
   Administrative operations over roles: creating new roles and managing their permission assignments. All endpoints require appropriate permissions.

5. **`health/`**
   Provides a health check endpoint for monitoring and infrastructure readiness checks.

## **III. Module Structure**

Each module follows an identical internal structure. Inline comments explaining the architectural pattern are provided only in `auth/` — since all modules are built the same way, documenting the same pattern repeatedly would be redundant.

Each module contains a `router.py` that defines the top-level router with its prefix and tags, and an `__init__.py` that imports the router and registers all feature routes onto it:

```
auth/
├── __init__.py        # Imports auth_router and registers all feature routes
├── router.py          # Defines auth_router with prefix and tags
├── login/
├── logout/
├── refresh/
└── register/
```

Each feature directory follows the same layout:

```
login/
├── __init__.py
├── domen.py           # Business logic and database operations
├── routes.py          # FastAPI route handler
└── schemas.py         # Pydantic request and response models
```