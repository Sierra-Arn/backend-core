# app/shared/postgres/db/roles.py
from enum import StrEnum


class RoleEnum(StrEnum):
    """
    Enumeration of all roles available in the application.

    Attributes
    ----------
    USER : str
        Default role assigned automatically to every newly registered account.
    ADMIN : str
        Privileged role reserved for administrative operations.
    """
    USER = "user"
    ADMIN = "admin"