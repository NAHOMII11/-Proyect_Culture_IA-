from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

# DTO de entrada para registro
class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "viewer"

# DTO de entrada para login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# DTO de salida con datos del usuario
class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# DTO de respuesta del token JWT
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"