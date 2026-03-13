#!/bin/bash

# =====================================================
# Strict Mode Flags:
#   -e: Exit immediately if any command exits with non-zero status
#   -u: Treat unset variables as an error
# =====================================================
set -eu

# Load .env file
if [[ -f .env ]]; then
    source .env
else
    echo "Error: .env file not found."
    exit 1
fi

# Generate ACL file using environment variables
cat > app/shared/redis/initialization/01-create-users.acl << EOF
user ${REDIS_ADMIN_NAME} on >${REDIS_ADMIN_PASSWORD} ~* &* +@all
user ${REDIS_USER_NAME} on >${REDIS_USER_PASSWORD} ~* +get +set +del +exists +expire +pexpire +ttl +pttl +mget +mset +setex +zadd +zcard +zremrangebyscore +ping
user default off nopass
EOF