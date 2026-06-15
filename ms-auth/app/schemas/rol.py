from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PermisoResumen(BaseModel):
    id: int
    codigo: str
    nombre: str
    modulo: str
    model_config = ConfigDict(from_attributes=True)


class AuditoriaSchema(BaseModel):
    activo: bool = True


class AuditoriaResponse(BaseModel):
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


class RolBase(AuditoriaSchema):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    descripcion: str | None = None


class RolCreate(RolBase):
    pass


class RolUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=50)
    nombre: str | None = Field(None, max_length=150)
    descripcion: str | None = None
    activo: bool | None = None


class RolResponse(RolBase, AuditoriaResponse):
    id: int
    permisos: list[PermisoResumen] = []
    model_config = ConfigDict(from_attributes=True)


class AsignarPermisosRequest(BaseModel):
    permiso_ids: list[int] = Field(..., min_length=1)
