from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AuditoriaSchema(BaseModel):
    activo: bool = True


class AuditoriaResponse(BaseModel):
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


class CuentaPorCobrarCreate(BaseModel):
    referencia_tipo: str | None = None
    referencia_id: int | None = None
    tercero_id: int | None = None
    tercero_tipo: str | None = None
    monto: Decimal = Field(..., gt=0)
    fecha_vencimiento: str | None = None
    descripcion: str | None = None


class CuentaPorCobrarResponse(AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    referencia_tipo: str | None
    referencia_id: int | None
    tercero_id: int | None
    tercero_tipo: str | None
    monto: Decimal
    saldo: Decimal
    estado: str
    fecha_vencimiento: str | None
    descripcion: str | None


class CuentaPorPagarCreate(BaseModel):
    referencia_tipo: str | None = None
    referencia_id: int | None = None
    tercero_id: int | None = None
    tercero_tipo: str | None = None
    monto: Decimal = Field(..., gt=0)
    fecha_vencimiento: str | None = None
    descripcion: str | None = None


class CuentaPorPagarResponse(AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    referencia_tipo: str | None
    referencia_id: int | None
    tercero_id: int | None
    tercero_tipo: str | None
    monto: Decimal
    saldo: Decimal
    estado: str
    fecha_vencimiento: str | None
    descripcion: str | None


class CobroCreate(BaseModel):
    cuenta_cobrar_id: int
    monto: Decimal = Field(..., gt=0)
    metodo: str = "EFECTIVO"
    referencia: str | None = None
    fecha: str | None = None


class CobroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cuenta_cobrar_id: int
    monto: Decimal
    metodo: str
    referencia: str | None
    fecha: str | None


class PagoCreate(BaseModel):
    cuenta_pagar_id: int
    monto: Decimal = Field(..., gt=0)
    metodo: str = "TRANSFERENCIA"
    referencia: str | None = None
    fecha: str | None = None


class PagoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cuenta_pagar_id: int
    monto: Decimal
    metodo: str
    referencia: str | None
    fecha: str | None


class CajaBase(BaseModel):
    codigo: str
    nombre: str


class CajaCreate(CajaBase, AuditoriaSchema):
    saldo: Decimal = Decimal("0")


class CajaUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    activo: bool | None = None


class CajaResponse(CajaBase, AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int
    saldo: Decimal


class BancoBase(BaseModel):
    codigo: str
    nombre: str


class BancoCreate(BancoBase, AuditoriaSchema):
    pass


class BancoUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    activo: bool | None = None


class BancoResponse(BancoBase, AuditoriaResponse):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MovimientoCajaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    caja_id: int
    tipo: str
    monto: Decimal
    referencia: str | None
    observaciones: str | None


class MovimientoBancarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cuenta_bancaria_id: int
    tipo: str
    monto: Decimal
    referencia: str | None
    observaciones: str | None
