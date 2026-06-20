from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


# ── Detalle cotización (módulo existente) ──────────────────

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


# ── Orden de compra ────────────────────────────────────────

class OrdenCompraDetalleCreate(BaseModel):
    producto_id: int = Field(..., gt=0)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)


class OrdenCompraDetalleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    producto_codigo: str | None = None
    producto_nombre: str | None = None
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal: Decimal


class OrdenCompraCreate(BaseModel):
    proveedor_id: int = Field(..., gt=0)
    cotizacion_id: int | None = None
    fecha: str | None = None
    observacion: str | None = None
    detalles: list[OrdenCompraDetalleCreate] = Field(..., min_length=1)

    @field_validator("detalles")
    @classmethod
    def validar_total_positivo(cls, detalles: list[OrdenCompraDetalleCreate]) -> list[OrdenCompraDetalleCreate]:
        total = sum(d.cantidad * d.precio_unitario for d in detalles)
        if total < 0:
            raise ValueError("El total de la orden no puede ser negativo")
        return detalles


class OrdenCompraUpdate(BaseModel):
    proveedor_id: int | None = Field(None, gt=0)
    cotizacion_id: int | None = None
    fecha: str | None = None
    observacion: str | None = None
    detalles: list[OrdenCompraDetalleCreate] | None = None

    @field_validator("detalles")
    @classmethod
    def validar_total_positivo(
        cls, detalles: list[OrdenCompraDetalleCreate] | None
    ) -> list[OrdenCompraDetalleCreate] | None:
        if detalles is None:
            return detalles
        total = sum(d.cantidad * d.precio_unitario for d in detalles)
        if total < 0:
            raise ValueError("El total de la orden no puede ser negativo")
        return detalles


class OrdenCompraResponse(AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    codigo: str
    proveedor_id: int
    cotizacion_id: int | None = None
    estado: str
    fecha: str | None = None
    observacion: str | None = Field(None, validation_alias="observaciones")
    total: Decimal
    detalles: list[OrdenCompraDetalleResponse] = []


# Alias retrocompatibles
OrdenDetalleCreate = OrdenCompraDetalleCreate
OrdenDetalleResponse = OrdenCompraDetalleResponse


# ── Recepción de compra ────────────────────────────────────

class RecepcionCompraDetalleCreate(BaseModel):
    producto_id: int = Field(..., gt=0)
    cantidad_recibida: Decimal = Field(..., gt=0)
    costo_unitario: Decimal = Field(..., ge=0)


class RecepcionCompraDetalleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    producto_codigo: str | None = None
    producto_nombre: str | None = None
    cantidad_recibida: Decimal
    costo_unitario: Decimal
    subtotal: Decimal


class RecepcionCompraCreate(BaseModel):
    orden_compra_id: int = Field(..., gt=0)
    almacen_id: int = Field(..., gt=0)
    fecha: str | None = None
    observacion: str | None = None
    detalles: list[RecepcionCompraDetalleCreate] = Field(..., min_length=1)

    @field_validator("detalles")
    @classmethod
    def validar_total_positivo(
        cls, detalles: list[RecepcionCompraDetalleCreate]
    ) -> list[RecepcionCompraDetalleCreate]:
        total = sum(d.cantidad_recibida * d.costo_unitario for d in detalles)
        if total < 0:
            raise ValueError("El total de la recepción no puede ser negativo")
        return detalles


class RecepcionCompraUpdate(BaseModel):
    almacen_id: int | None = Field(None, gt=0)
    fecha: str | None = None
    observacion: str | None = None
    detalles: list[RecepcionCompraDetalleCreate] | None = None

    @field_validator("detalles")
    @classmethod
    def validar_total_positivo(
        cls, detalles: list[RecepcionCompraDetalleCreate] | None
    ) -> list[RecepcionCompraDetalleCreate] | None:
        if detalles is None:
            return detalles
        total = sum(d.cantidad_recibida * d.costo_unitario for d in detalles)
        if total < 0:
            raise ValueError("El total de la recepción no puede ser negativo")
        return detalles


class RecepcionCompraResponse(AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    codigo: str
    orden_compra_id: int = Field(validation_alias="orden_id")
    almacen_id: int
    almacen_nombre: str | None = None
    sucursal_id: int | None = None
    sucursal_nombre: str | None = None
    compania_id: int | None = None
    compania_nombre: str | None = None
    estado: str
    fecha: str | None = None
    observacion: str | None = Field(None, validation_alias="observaciones")
    total: Decimal
    detalles: list[RecepcionCompraDetalleResponse] = []


# Alias retrocompatibles
RecepcionDetalleCreate = RecepcionCompraDetalleCreate
RecepcionDetalleResponse = RecepcionCompraDetalleResponse
