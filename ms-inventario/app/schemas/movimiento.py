from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.enums.tipo_movimiento import TipoMovimiento


class MovimientoInventarioResponse(BaseModel):
    id: int
    tipo: TipoMovimiento
    producto_id: int
    almacen_id: int
    cantidad: Decimal
    cantidad_anterior: Decimal
    cantidad_nueva: Decimal
    referencia_tipo: str | None = None
    referencia_id: int | None = None
    observaciones: str | None = None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class KardexResponse(BaseModel):
    producto_id: int
    total_movimientos: int
    movimientos: list[MovimientoInventarioResponse]
