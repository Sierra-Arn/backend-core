# app/modules/roles/router.py
from fastapi import APIRouter

roles_router = APIRouter(prefix="/roles", tags=["roles"])