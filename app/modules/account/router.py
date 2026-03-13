# app/modules/account/router.py
from fastapi import APIRouter

account_router = APIRouter(prefix="/account", tags=["account"])