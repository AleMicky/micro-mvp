from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categoria import AuditoriaResponse, AuditoriaSchema


class ProductoBase(AuditoriaSchema):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)
    descripcion: str | None = None
    categoria_id: int
    marca_id: int | None = None
    unidad_medida_id: int


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=50)
    nombre: str | None = Field(None, max_length=200)
    descripcion: str | None = None
    categoria_id: int | None = None
    marca_id: int | None = None
    unidad_medida_id: int | None = None
    activo: bool | None = None


class ProductoResponse(ProductoBase, AuditoriaResponse):
    id: int
    model_config = ConfigDict(from_attributes=True)
