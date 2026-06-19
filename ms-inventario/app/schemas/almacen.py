from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AuditoriaSchema(BaseModel):
    activo: bool = True


class AuditoriaResponse(BaseModel):
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


class AlmacenBase(AuditoriaSchema):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    direccion: str | None = None
    sucursal_id: int | None = None


class AlmacenCreate(AlmacenBase):
    pass


class AlmacenUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=50)
    nombre: str | None = Field(None, max_length=150)
    direccion: str | None = None
    sucursal_id: int | None = None
    activo: bool | None = None


class AlmacenResponse(AlmacenBase, AuditoriaResponse):
    id: int
    model_config = ConfigDict(from_attributes=True)
