from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.movimiento import MovimientoInventarioResponse


class AjusteDetalleResponse(BaseModel):
    id: int
    producto_id: int
    cantidad_anterior: Decimal
    cantidad_nueva: Decimal
    diferencia: Decimal
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class AjusteInventarioResponse(BaseModel):
    id: int
    codigo: str | None
    almacen_id: int
    motivo: str | None
    observaciones: str | None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
    detalles: list[AjusteDetalleResponse]
    movimientos: list[MovimientoInventarioResponse] = []
    model_config = ConfigDict(from_attributes=True)


class TransferenciaDetalleResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: Decimal
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class TransferenciaInventarioResponse(BaseModel):
    id: int
    codigo: str | None
    almacen_origen_id: int
    almacen_destino_id: int
    estado: str
    observaciones: str | None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
    detalles: list[TransferenciaDetalleResponse]
    movimientos: list[MovimientoInventarioResponse] = []
    model_config = ConfigDict(from_attributes=True)


class StockOperacionResponse(BaseModel):
    existencia_id: int
    producto_id: int
    almacen_id: int
    cantidad_anterior: Decimal
    cantidad_nueva: Decimal
    movimiento: MovimientoInventarioResponse
