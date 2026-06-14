from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categoria import AuditoriaResponse, AuditoriaSchema


class UnidadMedidaBase(AuditoriaSchema):
    codigo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=100)
    abreviatura: str = Field(..., max_length=10)


class UnidadMedidaCreate(UnidadMedidaBase):
    pass


class UnidadMedidaUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=20)
    nombre: str | None = Field(None, max_length=100)
    abreviatura: str | None = Field(None, max_length=10)
    activo: bool | None = None


class UnidadMedidaResponse(UnidadMedidaBase, AuditoriaResponse):
    id: int
    model_config = ConfigDict(from_attributes=True)
