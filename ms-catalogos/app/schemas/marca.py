from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categoria import AuditoriaResponse, AuditoriaSchema


class MarcaBase(AuditoriaSchema):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    descripcion: str | None = None


class MarcaCreate(MarcaBase):
    pass


class MarcaUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=50)
    nombre: str | None = Field(None, max_length=150)
    descripcion: str | None = None
    activo: bool | None = None


class MarcaResponse(MarcaBase, AuditoriaResponse):
    id: int
    model_config = ConfigDict(from_attributes=True)
