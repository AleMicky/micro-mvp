from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AuditoriaSchema(BaseModel):
    activo: bool = True


class AuditoriaResponse(BaseModel):
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


# ── Proveedor ──────────────────────────────────────────────

class ProveedorBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)
    rfc: str | None = None
    email: str | None = None
    telefono: str | None = None
    direccion: str | None = None


class ProveedorCreate(ProveedorBase, AuditoriaSchema):
    pass


class ProveedorUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    rfc: str | None = None
    email: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    activo: bool | None = None


class ProveedorResponse(ProveedorBase, AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ── Detalle cotización ─────────────────────────────────────

class CotizacionDetalleBase(BaseModel):
    producto_id: int
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)


class CotizacionDetalleCreate(CotizacionDetalleBase):
    pass


class CotizacionDetalleResponse(CotizacionDetalleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subtotal: Decimal


# ── Cotización ─────────────────────────────────────────────

class CotizacionCompraBase(BaseModel):
    proveedor_id: int
    fecha: str | None = None
    observaciones: str | None = None
    estado: str = "BORRADOR"


class CotizacionCompraCreate(CotizacionCompraBase):
    detalles: list[CotizacionDetalleCreate] = Field(..., min_length=1)


class CotizacionCompraUpdate(BaseModel):
    proveedor_id: int | None = None
    fecha: str | None = None
    observaciones: str | None = None
    estado: str | None = None
    activo: bool | None = None
    detalles: list[CotizacionDetalleCreate] | None = None


class CotizacionCompraResponse(CotizacionCompraBase, AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    total: Decimal
    detalles: list[CotizacionDetalleResponse] = []


# ── Detalle orden ──────────────────────────────────────────

class OrdenDetalleBase(BaseModel):
    producto_id: int
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)


class OrdenDetalleCreate(OrdenDetalleBase):
    pass


class OrdenDetalleResponse(OrdenDetalleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subtotal: Decimal


# ── Orden compra ───────────────────────────────────────────

class OrdenCompraBase(BaseModel):
    proveedor_id: int
    cotizacion_id: int | None = None
    fecha: str | None = None
    observaciones: str | None = None
    estado: str = "BORRADOR"


class OrdenCompraCreate(OrdenCompraBase):
    detalles: list[OrdenDetalleCreate] = Field(..., min_length=1)


class OrdenCompraUpdate(BaseModel):
    proveedor_id: int | None = None
    cotizacion_id: int | None = None
    fecha: str | None = None
    observaciones: str | None = None
    estado: str | None = None
    activo: bool | None = None
    detalles: list[OrdenDetalleCreate] | None = None


class OrdenCompraResponse(OrdenCompraBase, AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    total: Decimal
    detalles: list[OrdenDetalleResponse] = []


# ── Recepción ──────────────────────────────────────────────

class RecepcionDetalleBase(BaseModel):
    producto_id: int
    cantidad: Decimal = Field(..., gt=0)


class RecepcionDetalleCreate(RecepcionDetalleBase):
    pass


class RecepcionDetalleResponse(RecepcionDetalleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RecepcionCompraCreate(BaseModel):
    orden_id: int
    almacen_id: int
    fecha: str | None = None
    observaciones: str | None = None
    detalles: list[RecepcionDetalleCreate] = Field(..., min_length=1)


class RecepcionCompraResponse(AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    orden_id: int
    almacen_id: int
    estado: str
    fecha: str | None
    observaciones: str | None
    detalles: list[RecepcionDetalleResponse] = []
