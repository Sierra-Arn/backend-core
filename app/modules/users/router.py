# app/modules/users/router.py
from fastapi import APIRouter

users_router = APIRouter(prefix="/users", tags=["users"])