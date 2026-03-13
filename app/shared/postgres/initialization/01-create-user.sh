#!/bin/bash

# =====================================================
# Strict Mode Flags:
#   -e: Exit immediately if any command exits with non-zero status
#   -u: Treat unset variables as an error
# =====================================================
set -eu

# Wait for PostgreSQL server to be ready before proceeding
# pg_isready checks if PostgreSQL is accepting connections
until pg_isready -U "$POSTGRES_USER"; do
  sleep 1
done

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create dedicated application user (non-superuser for security)
    CREATE USER "$POSTGRES_USER_NAME" WITH PASSWORD '$POSTGRES_USER_PASSWORD';
    
    -- Create application database
    CREATE DATABASE "$POSTGRES_USER_DB_NAME";
    
    -- Grant all privileges on the created database (not on the entire server) to application user
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_USER_DB_NAME" TO "$POSTGRES_USER_NAME";
    
    -- Make application user the owner of the database
    ALTER DATABASE "$POSTGRES_USER_DB_NAME" OWNER TO "$POSTGRES_USER_NAME";
EOSQL