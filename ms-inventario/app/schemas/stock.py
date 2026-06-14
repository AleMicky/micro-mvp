from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class StockOperacionBase(BaseModel):
    producto_id: int = Field(..., gt=0)
    almacen_id: int = Field(..., gt=0)
    cantidad: Decimal = Field(..., gt=0)
    observaciones: str | None = None


class StockIngresoRequest(StockOperacionBase):
    stock_minimo: Decimal | None = Field(None, ge=0)
    stock_maximo: Decimal | None = Field(None, ge=0)


class StockSalidaRequest(StockOperacionBase):
    pass


class AjusteDetalleRequest(BaseModel):
    producto_id: int = Field(..., gt=0)
    cantidad_nueva: Decimal = Field(..., ge=0)


class StockAjusteRequest(BaseModel):
    almacen_id: int = Field(..., gt=0)
    motivo: str | None = None
    observaciones: str | None = None
    detalles: list[AjusteDetalleRequest] = Field(..., min_length=1)


class TransferenciaDetalleRequest(BaseModel):
    producto_id: int = Field(..., gt=0)
    cantidad: Decimal = Field(..., gt=0)


class StockTransferenciaRequest(BaseModel):
    almacen_origen_id: int = Field(..., gt=0)
    almacen_destino_id: int = Field(..., gt=0)
    observaciones: str | None = None
    detalles: list[TransferenciaDetalleRequest] = Field(..., min_length=1)

    @field_validator("almacen_destino_id")
    @classmethod
    def almacenes_distintos(cls, destino: int, info) -> int:
        origen = info.data.get("almacen_origen_id")
        if origen is not None and origen == destino:
            raise ValueError("El almacén origen y destino deben ser diferentes")
        return destino
