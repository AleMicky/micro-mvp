from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RolResumen(BaseModel):
    id: int
    codigo: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class UsuarioBase(BaseModel):
    nombre_completo: str = Field(..., max_length=200)
    nombre_usuario: str = Field(..., max_length=100)
    correo: EmailStr
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)


class UsuarioUpdate(BaseModel):
    nombre_completo: str | None = Field(None, max_length=200)
    nombre_usuario: str | None = Field(None, max_length=100)
    correo: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    activo: bool | None = None


class UsuarioResponse(UsuarioBase):
    id: int
    ultimo_login_en: datetime | None
    roles: list[RolResumen] = []
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class AsignarRolesRequest(BaseModel):
    rol_ids: list[int] = Field(..., min_length=1)
