from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categoria import AuditoriaResponse, AuditoriaSchema


class ProductoBase(AuditoriaSchema):
    codigo: str = Field(..., max_length=50)
    codigo_barras: str | None = Field(None, max_length=50)
    nombre: str = Field(..., max_length=200)
    descripcion: str | None = None
    categoria_id: int
    marca_id: int | None = None
    unidad_medida_id: int
    precio_base: Decimal = Field(default=Decimal("0"), ge=0)
    imagen_url: str | None = None
    estado: str = Field(default="ACTIVO", max_length=30)


class ProductoCreate(ProductoBase):
    precio_venta: Decimal | None = Field(None, gt=0)


class ProductoUpdate(BaseModel):
    codigo: str | None = Field(None, max_length=50)
    codigo_barras: str | None = Field(None, max_length=50)
    nombre: str | None = Field(None, max_length=200)
    descripcion: str | None = None
    categoria_id: int | None = None
    marca_id: int | None = None
    unidad_medida_id: int | None = None
    precio_base: Decimal | None = Field(None, ge=0)
    imagen_url: str | None = None
    estado: str | None = Field(None, max_length=30)
    activo: bool | None = None


class ProductoResponse(ProductoBase, AuditoriaResponse):
    id: int
    precio_actual: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductoImagenResponse(BaseModel):
    imagen_url: str
