"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr


class MagicLinkRequest(BaseModel):
    email: EmailStr


class VerifyRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str | None = None
    role: str = "user"


class UpdateUserRequest(BaseModel):
    display_name: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    sse_token: str
    token_type: str = "bearer"
    user: UserResponse
