# app/modules/users/__init__.py
from .router import users_router
from .get_all import get_all_route
from .manage_roles import assign_role_route, revoke_role_route