from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditoriaSchema(BaseModel):
    activo: bool = True


class AuditoriaResponse(BaseModel):
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


class SucursalSnapshot(BaseModel):
    id: int
    codigo: str
    nombre: str


class CompaniaSnapshot(BaseModel):
    id: int
    nombre: str


class AlmacenBase(AuditoriaSchema):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    direccion: str | None = None
    latitud: float | None = Field(None, ge=-90, le=90)
    longitud: float | None = Field(None, ge=-180, le=180)


class AlmacenCreate(AlmacenBase):
    sucursal_id: int | None = None


class AlmacenUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=50)
    nombre: str | None = Field(None, max_length=150)
    direccion: str | None = None
    latitud: float | None = Field(None, ge=-90, le=90)
    longitud: float | None = Field(None, ge=-180, le=180)
    activo: bool | None = None
    sucursal_id: int | None = None


class AlmacenResponse(AlmacenBase, AuditoriaResponse):
    id: int
    sucursal_id: int | None = None
    sucursal_codigo: str | None = None
    sucursal_nombre: str | None = None
    compania_id: int | None = None
    compania_nombre: str | None = None
    sucursal: SucursalSnapshot | None = None
    compania: CompaniaSnapshot | None = None
    model_config = ConfigDict(from_attributes=True)
