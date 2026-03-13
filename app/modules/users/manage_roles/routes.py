# app/modules/users/manage_roles/routes.py
from fastapi import Depends, status
from .schemas import AssignRoleRequest
from .domen import assign_role, revoke_role
from ..router import users_router
from ....shared.auth.dependencies import require_permission


@users_router.post(
    "/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign a role to a user",
    description=(
        "Assigns the specified role to the target user. "
        "Restricted to users with the ``users:manage_roles`` permission. "
        "Returns ``404`` if the user or role does not exist, "
        "``409`` if the user already has the role."
    ),
)
async def assign_role_route(
    user_id: int,
    body: AssignRoleRequest,
    payload: dict = Depends(require_permission("users:manage_roles")),
) -> None:
    await assign_role(user_id=user_id, role_name=body.role_name)


@users_router.delete(
    "/{user_id}/roles/{role_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a role from a user",
    description=(
        "Removes the specified role from the target user. "
        "Restricted to users with the ``users:manage_roles`` permission. "
        "Returns ``404`` if the user or role does not exist, "
        "``409`` if the user does not have the role."
    ),
)
async def revoke_role_route(
    user_id: int,
    role_name: str,
    payload: dict = Depends(require_permission("users:manage_roles")),
) -> None:
    await revoke_role(user_id=user_id, role_name=role_name)