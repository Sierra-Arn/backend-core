# app/modules/roles/__init__.py
from .router import roles_router
from .create import create_role_route
from .manage_permissions import assign_permission_route, revoke_permission_route