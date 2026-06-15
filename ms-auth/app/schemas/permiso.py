from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditoriaSchema(BaseModel):
    activo: bool = True


class AuditoriaResponse(BaseModel):
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


class PermisoBase(AuditoriaSchema):
    codigo: str = Field(..., max_length=80)
    nombre: str = Field(..., max_length=150)
    modulo: str = Field(..., max_length=50)
    descripcion: str | None = None


class PermisoCreate(PermisoBase):
    pass


class PermisoUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=80)
    nombre: str | None = Field(None, max_length=150)
    modulo: str | None = Field(None, max_length=50)
    descripcion: str | None = None
    activo: bool | None = None


class PermisoResponse(PermisoBase, AuditoriaResponse):
    id: int
    model_config = ConfigDict(from_attributes=True)
