from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class AuditoriaSchema(BaseModel):
    activo: bool = True

class AuditoriaResponse(BaseModel):
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

class ClienteBase(BaseModel):
    codigo: str
    nombre: str
    rfc: str | None = None
    email: str | None = None
    telefono: str | None = None
    direccion: str | None = None

class ClienteCreate(ClienteBase, AuditoriaSchema):
    pass

class ClienteUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    rfc: str | None = None
    email: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    activo: bool | None = None

class ClienteResponse(ClienteBase, AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int

class DetalleBase(BaseModel):
    producto_id: int
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)

class DetalleCreate(DetalleBase):
    pass

class DetalleResponse(DetalleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subtotal: Decimal

class CotizacionVentaBase(BaseModel):
    cliente_id: int
    fecha: str | None = None
    observaciones: str | None = None
    estado: str = "BORRADOR"

class CotizacionVentaCreate(CotizacionVentaBase):
    detalles: list[DetalleCreate] = Field(..., min_length=1)

class CotizacionVentaUpdate(BaseModel):
    cliente_id: int | None = None
    fecha: str | None = None
    observaciones: str | None = None
    estado: str | None = None
    activo: bool | None = None
    detalles: list[DetalleCreate] | None = None

class CotizacionVentaResponse(CotizacionVentaBase, AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    total: Decimal
    detalles: list[DetalleResponse] = []

class VentaBase(BaseModel):
    cliente_id: int
    cotizacion_id: int | None = None
    almacen_id: int = 1
    fecha: str | None = None
    observaciones: str | None = None
    estado: str = "BORRADOR"

class VentaCreate(VentaBase):
    detalles: list[DetalleCreate] = Field(..., min_length=1)

class VentaUpdate(BaseModel):
    cliente_id: int | None = None
    almacen_id: int | None = None
    fecha: str | None = None
    observaciones: str | None = None
    estado: str | None = None
    activo: bool | None = None
    detalles: list[DetalleCreate] | None = None

class VentaResponse(VentaBase, AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    total: Decimal
    detalles: list[DetalleResponse] = []

class FacturaCreate(BaseModel):
    venta_id: int
    fecha: str | None = None
    impuesto: Decimal = Decimal("0")

class FacturaResponse(AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    venta_id: int
    estado: str
    fecha: str | None
    subtotal: Decimal
    impuesto: Decimal
    total: Decimal
    detalles: list[DetalleResponse] = []
