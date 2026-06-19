# Backend Core

*An educational project demonstrating how to build a backend server with Python, covering authentication, authorization, rate limiting, access logging and global error handling.*

## Project Structure

```
backend-core/
├── packages/                     # Monorepo root containing all independently deployable Python modules and
│   │                             # shared libraries. Each package strictly follows the standard `src/` layout
│   │                             # (e.g., `packages/server/src/server/`) for clean imports and packaging.
│   │
│   ├── server/                   # FastAPI application handling HTTP routing, request validation,
│   │                             # authentication, authorization, rate limiting, access logging,
│   │                             # and global error handling.
│   │
│   ├── shared/                   # Cross-process shared infrastructure. Contains base configurations
│   │                             # and unified client abstractions for external services
│   │                             # (e.g., PostgreSQL, Redis).
│   │
│   └── scripts/                  # Standalone automation scripts for environment bootstrapping,
│                                 # infrastructure initialization, and auxiliary utility tasks.
│
├── docs/                         # Technical documentation covering project dependencies,
│                                 # codebase layout, and request flow diagrams for every endpoint.
|
├── migrations/                   # Alembic migration environment and database schema change scripts.
│
├── docker-compose.yml            # Docker Compose stack for running infrastructure services
│                                 # (PostgreSQL, Redis) locally.
│
├── .env.example                  # Environment variable template. Copied to .env during bootstrapping
│                                 # with auto-generated credentials for credential fields.
│
├── pixi.toml                     # Pixi environment configuration defining dependency groups.
│
├── pixi.lock                     # Fully resolved and reproducible dependency lockfile.
│
└── justfile                      # Task runner: bootstrap commands, database migration targets,
                                  # runtime process launchers, and Docker Compose shortcuts.
                                  # Automatically manages pixi environment context per recipe.
```

## Quick Start

### I. Prerequisites

- [Pixi](https://pixi.sh/latest/) package manager.
- [Docker and Docker Compose](https://docs.docker.com/engine/install/).
- GNU/Linux-based system on `x86_64` architecture.

> **Note:**  
> These prerequisites are not strict requirements but describe the environment used for development. The service can be set up in alternative environments with different package managers, operating systems, or tools for running applications in isolated containers if needed.

### II. Setup

1. **Clone the repository**

    ```bash
    git clone git@github.com:Sierra-Arn/backend-core.git
    cd backend-core
    ```

2. **Install dependencies**

    ```bash
    pixi install
    ```

3. **Activate environment**

    ```bash
    pixi shell
    ```

### III. Launch

Once the environment is activated, the service can be launched with a single command:

```bash
just quick-start
```

The launch script will automatically execute all necessary setup steps, start the server, and open the Swagger UI in your default web browser once the API is ready.

> **Want to see what happens under the hood?**  
> The launch script is fully documented with step-by-step comments explaining each action. You can find it here:
> - [Quick start script](./packages/scripts/src/scripts/quick_start.py)

### IV. Cleanup

When you are done, shut down the running services by terminating the server terminal process, then bring down the infrastructure containers:

```bash
just docker-down
```

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).