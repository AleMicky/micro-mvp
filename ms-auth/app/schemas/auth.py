from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    identificador: str = Field(..., description="Nombre de usuario o correo electrónico")
    password: str = Field(..., min_length=6)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    nombre_completo: str = Field(..., max_length=200)
    nombre_usuario: str = Field(..., max_length=100)
    correo: EmailStr
    password: str = Field(..., min_length=8)


class MeResponse(BaseModel):
    id: int
    nombre_completo: str
    nombre_usuario: str
    correo: str
    activo: bool
    ultimo_login_en: datetime | None
    roles: list[str]
    permisos: list[str]
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)
