from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditoriaSchema(BaseModel):
    activo: bool = True


class AuditoriaResponse(BaseModel):
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


class CiudadBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    departamento: str | None = None


class CiudadCreate(CiudadBase, AuditoriaSchema):
    pass


class CiudadUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=150)
    departamento: str | None = None
    activo: bool | None = None


class CiudadResponse(CiudadBase, AuditoriaResponse):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CompaniaBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)
    nit: str | None = None
    direccion: str | None = None
    telefono: str | None = None


class CompaniaCreate(CompaniaBase, AuditoriaSchema):
    pass


class CompaniaUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=50)
    nombre: str | None = Field(None, max_length=200)
    nit: str | None = None
    direccion: str | None = None
    telefono: str | None = None
    activo: bool | None = None


class CompaniaResponse(CompaniaBase, AuditoriaResponse):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SucursalBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)
    compania_id: int
    ciudad_id: int
    direccion: str | None = None


class SucursalCreate(SucursalBase, AuditoriaSchema):
    pass


class SucursalUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=50)
    nombre: str | None = Field(None, max_length=200)
    compania_id: int | None = None
    ciudad_id: int | None = None
    direccion: str | None = None
    activo: bool | None = None


class SucursalResponse(SucursalBase, AuditoriaResponse):
    id: int
    model_config = ConfigDict(from_attributes=True)
