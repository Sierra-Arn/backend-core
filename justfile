# =====================================================
# Justfile Settings
# =====================================================
# Load environment variables from .env file into justfile context
# This allows justfile recipes to reference variables using ${VAR_NAME} syntax
set dotenv-load := true

# Export all loaded environment variables to child processes
# This makes variables available to all commands executed within recipes
# (e.g., docker compose, shell scripts, and other external tools)
set export := true


# =====================================================
# General Setup
# =====================================================

# Create local environment configuration file from template
# Copy .env.example to .env for initial project setup
# After copying, edit .env file to set your specific configuration values
copy-env:
    cp .env.example .env


# Make initialization scripts executable
# Grants execute permissions to the user creation shell scripts
# Required for running the script during container startups
make-x:  
    chmod +x app/shared/redis/initialization/generate-redis-acl.sh
    chmod +x app/shared/postgres/initialization/01-create-user.sh

# Generate Redis ACL configuration file  
# Executes the ACL script to produce 01-create-users.acl based on current .env settings  
# Output file will be mounted into the Redis container for authentication and access control  
gen-acl:  
    app/shared/redis/initialization/generate-redis-acl.sh


# =====================================================
# Python-based Infrastructure Management
# =====================================================

# Create a new Alembic migration revision with auto-generated changes
# Detects model changes and generates a new migration script in the migrations directory
# Accepts an optional migration message as the first argument (defaults to "Auto migration")
# Example usage:
#   just alembic-revision
#   just alembic-revision "Hello, World!"
alembic-revision message="Auto migration":
    alembic -c ./app/shared/postgres/migrations/alembic.ini revision --autogenerate -m "{{ message }}"

# Create a new empty Alembic migration revision without auto-generated changes
# Useful for writing manual data migrations (e.g., seeding default records)
# Accepts an optional migration message as the first argument (defaults to "New migration")
alembic-migration message="New migration":
    alembic -c ./app/shared/postgres/migrations/alembic.ini revision -m "{{ message }}"

# Apply all pending migrations to bring the database schema up to the latest version
alembic-upgrade:
    alembic -c ./app/shared/postgres/migrations/alembic.ini upgrade head

# Revert the most recent migration to roll back the latest schema change
alembic-downgrade:
    alembic -c ./app/shared/postgres/migrations/alembic.ini downgrade -1

# Generate a cryptographically secure JWT secret key and print it
gen-jwt-key:
    python -m app.shared.auth.generate_jwt_secret_key

# Seed the database with default roles required for the application to operate
seed-db:
    python -m app.shared.postgres.db.seed

# Start server for REST API
api-up:
    uvicorn app:create_app --factory --reload --reload-dir app

# Export OpenAPI/Swagger specification for the API
export-swagger:
	python -m app.export_swagger


# =====================================================
# Docker Compose Services
# =====================================================

# Start all containers
containers-up:
    docker compose --env-file .env up -d

# Stop and remove all containers
containers-down:
    docker compose --env-file .env down