# app/shared/postgres/db/seed.py
"""
Database seeding script for the initial admin account.

Creates an admin user account if one does not already exist.
Safe to run multiple times — the existing account is never duplicated
or overwritten.

Usage
-----
Run once after Alembic migrations have been applied:

    python -m app.shared.postgres.db.seed
"""

import os
import asyncio
from dotenv import load_dotenv
from .session import get_async_db_session
from .repositories import UserRepository, RoleRepository, UserRoleRepository
from ...auth import hash_password

load_dotenv()


def _get_required_env(key: str) -> str:
    """
    Read a required environment variable.

    Parameters
    ----------
    key : str
        Name of the environment variable to read.

    Returns
    -------
    str
        The value of the environment variable.

    Raises
    ------
    RuntimeError
        If the variable is not set or is empty.
    """
    value = os.getenv(key)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{key}' is not set. "
            f"Make sure it is defined in your .env file before running the seed script."
        )
    return value


async def seed() -> None:
    """
    Create the initial admin account if it does not already exist.

    Reads ``SEED_ADMIN_EMAIL`` and ``SEED_ADMIN_PASSWORD`` from the
    environment. Looks up the ``admin`` role seeded by the Alembic
    migration, then creates a user account with the provided credentials
    and assigns the admin role to it. If the account already exists,
    the step is silently skipped.

    Raises
    ------
    RuntimeError
        If ``SEED_ADMIN_EMAIL`` or ``SEED_ADMIN_PASSWORD`` are not set,
        or if the ``admin`` role is not found in the database.
    """

    admin_email = _get_required_env("SEED_ADMIN_EMAIL")
    admin_password = _get_required_env("SEED_ADMIN_PASSWORD")

    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)
        user_role_repo = UserRoleRepository(db)

        print("Seeding admin account...")

        admin_role = await role_repo.get_by_name("admin")
        if admin_role is None:
            raise RuntimeError(
                "Admin role not found. Make sure Alembic migrations have been applied."
            )

        existing = await user_repo.get_by_email(admin_email)
        if existing is not None:
            print(f"  [=] Admin account '{admin_email}' already exists, skipping.")
        else:
            user = await user_repo.create({
                "email": admin_email,
                "hashed_password": hash_password(admin_password),
            })
            await user_role_repo.assign_role(user_id=user.id, role_id=admin_role.id)
            await db.commit()
            print(f"  [+] Admin account '{admin_email}' created.")

        print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())