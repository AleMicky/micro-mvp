from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExistenciaBase(BaseModel):
    producto_id: int = Field(..., gt=0)
    almacen_id: int = Field(..., gt=0)
    cantidad_actual: Decimal = Field(default=Decimal("0"), ge=0)
    stock_minimo: Decimal = Field(default=Decimal("0"), ge=0)
    stock_maximo: Decimal | None = Field(None, ge=0)


class ExistenciaResponse(ExistenciaBase):
    id: int
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)
