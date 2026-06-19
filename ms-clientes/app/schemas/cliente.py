from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ClienteBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)
    email: str | None = None
    telefono: str | None = None
    documento: str | None = None
    direccion: str | None = None
    activo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    email: str | None = None
    telefono: str | None = None
    documento: str | None = None
    direccion: str | None = None
    activo: bool | None = None


class ClienteResponse(ClienteBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class PuntosAsignarRequest(BaseModel):
    puntos: int = Field(..., gt=0)
    motivo: str | None = None
    referencia: str | None = None


class PuntosClienteResponse(BaseModel):
    id: int
    cliente_id: int
    puntos: int
    motivo: str | None
    referencia: str | None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class HistorialClienteResponse(BaseModel):
    id: int
    cliente_id: int
    tipo: str
    descripcion: str | None
    monto: Decimal | None
    referencia: str | None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class ClienteDetalleResponse(ClienteResponse):
    total_puntos: int = 0
    historial: list[HistorialClienteResponse] = []
