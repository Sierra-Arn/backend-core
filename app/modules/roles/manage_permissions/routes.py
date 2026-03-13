# app/modules/roles/manage_permissions/routes.py
from fastapi import Depends, status
from .schemas import AssignPermissionRequest
from .domen import assign_permission, revoke_permission
from ..router import roles_router
from ....shared.postgres.db.models import Permission
from ....shared.auth.dependencies import require_permission


@roles_router.post(
    "/{role_id}/permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign a permission to a role",
    description=(
        "Assigns the specified permission to the target role. "
        "Restricted to users with the ``roles:manage_permissions`` permission. "
        "Returns ``404`` if the role does not exist, "
        "``409`` if the role already has the permission."
    ),
)
async def assign_permission_route(
    role_id: int,
    body: AssignPermissionRequest,
    payload: dict = Depends(require_permission("roles:manage_permissions")),
) -> None:
    await assign_permission(role_id=role_id, permission=body.permission)


@roles_router.delete(
    "/{role_id}/permissions/{permission}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a permission from a role",
    description=(
        "Removes the specified permission from the target role. "
        "Restricted to users with the ``roles:manage_permissions`` permission. "
        "Returns ``404`` if the role does not exist, "
        "``409`` if the role does not have the permission."
    ),
)
async def revoke_permission_route(
    role_id: int,
    permission: Permission,
    payload: dict = Depends(require_permission("roles:manage_permissions")),
) -> None:
    await revoke_permission(role_id=role_id, permission=permission)