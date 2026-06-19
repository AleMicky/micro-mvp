from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PrecioProductoCreate(BaseModel):
    precio_venta: Decimal = Field(..., gt=0)


class PrecioProductoResponse(BaseModel):
    id: int
    producto_id: int
    precio_venta: Decimal
    fecha_inicio: datetime
    fecha_fin: datetime | None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
