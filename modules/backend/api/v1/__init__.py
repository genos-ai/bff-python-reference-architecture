"""
API Version 1 Router.

Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from modules.backend.api.v1.endpoints import auth, users

router = APIRouter()

router.include_router(auth.router, tags=["auth"])
router.include_router(users.router, tags=["users"])
