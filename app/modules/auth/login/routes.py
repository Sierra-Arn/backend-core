# app/modules/auth/login/routes.py
from fastapi import status
from .schemas import LoginRequest, LoginResponse
from .domen import login
from ..router import auth_router


# response_model tells FastAPI to use LoginResponse as the documented output
# schema for this endpoint — Swagger UI will render it as the expected response
# body under the 200 status code.
@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="Authenticate a user",
    description=(
        "Verifies the provided credentials and issues a new access/refresh "
        "token pair. Returns ``401`` if the email is not registered or the "
        "password is incorrect."
    ),
)
async def login_route(body: LoginRequest) -> LoginResponse:
    tokens = await login(email=body.email, password=body.password)
    return LoginResponse(**tokens)