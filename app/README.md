# **Application Structure**

*This README provides a high-level architectural overview of the application: what each component is for and why it exists. For implementation details refer to the dedicated `README.md` inside each directory and the inline comments within each file.*

## **I. Top-level files**

1. **`config.py`**
   Defines the API server configuration schema using Pydantic Settings, loaded from `.env` with the `API_` prefix. Controls server-level settings such as host, port, and OpenAPI documentation URLs.

2. **`export_swagger.py`**
   A utility script that exports the application's OpenAPI schema to an `openapi.yaml` file. Run manually when the schema needs to be updated.

3. **`__init__.py`**
   Application entry point. Defines the `create_app()` factory function that instantiates and configures the FastAPI application — registering exception handlers, middleware, and routers.

## **II. `modules/` — Feature Modules**

The application follows a **modular monolith** architecture, where each feature is encapsulated in its own self-contained module. Each module owns its routing, domain logic, and schemas, with no direct dependencies on other modules.

## **III. `shared/` — Shared Infrastructure**

Contains all infrastructure components shared across feature modules: database access, Redis client, authentication utilities, logging, middleware, and exception handlers. Modules depend on `shared/`, but `shared/` never depends on modules.