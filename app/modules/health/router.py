# app/modules/health/router.py
from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["health"])