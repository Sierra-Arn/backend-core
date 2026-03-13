# app/shared/postgres/db/repositories/__init__.py
from .base import BaseRepository 
from .user import UserRepository
from .role import RoleRepository
from .user_role import UserRoleRepository
from .role_permission import RolePermissionRepository
from .refresh_token import RefreshTokenRepository