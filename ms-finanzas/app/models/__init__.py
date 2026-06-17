from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class CuentaPorCobrar(Base, AuditoriaMixin):
    __tablename__ = "cuentas_por_cobrar"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    referencia_tipo: Mapped[str | None] = mapped_column(String(50))
    referencia_id: Mapped[int | None] = mapped_column()
    tercero_id: Mapped[int | None] = mapped_column()
    tercero_tipo: Mapped[str | None] = mapped_column(String(30))
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE", nullable=False)
    fecha_vencimiento: Mapped[str | None] = mapped_column(String(10))
    descripcion: Mapped[str | None] = mapped_column(Text)


class CuentaPorPagar(Base, AuditoriaMixin):
    __tablename__ = "cuentas_por_pagar"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    referencia_tipo: Mapped[str | None] = mapped_column(String(50))
    referencia_id: Mapped[int | None] = mapped_column()
    tercero_id: Mapped[int | None] = mapped_column()
    tercero_tipo: Mapped[str | None] = mapped_column(String(30))
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE", nullable=False)
    fecha_vencimiento: Mapped[str | None] = mapped_column(String(10))
    descripcion: Mapped[str | None] = mapped_column(Text)


class Caja(Base, AuditoriaMixin):
    __tablename__ = "cajas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)


class MovimientoCaja(Base):
    __tablename__ = "movimientos_caja"

    id: Mapped[int] = mapped_column(primary_key=True)
    caja_id: Mapped[int] = mapped_column(ForeignKey("cajas.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    referencia: Mapped[str | None] = mapped_column(String(100))
    observaciones: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[str] = mapped_column(String(30))

    caja: Mapped["Caja"] = relationship("Caja")


class Banco(Base, AuditoriaMixin):
    __tablename__ = "bancos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)


class CuentaBancaria(Base, AuditoriaMixin):
    __tablename__ = "cuentas_bancarias"

    id: Mapped[int] = mapped_column(primary_key=True)
    banco_id: Mapped[int] = mapped_column(ForeignKey("bancos.id"), nullable=False)
    numero_cuenta: Mapped[str] = mapped_column(String(50), nullable=False)
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    banco: Mapped["Banco"] = relationship("Banco")


class MovimientoBancario(Base):
    __tablename__ = "movimientos_bancarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    cuenta_bancaria_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bancarias.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    referencia: Mapped[str | None] = mapped_column(String(100))
    observaciones: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[str] = mapped_column(String(30))


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True)
    cuenta_pagar_id: Mapped[int] = mapped_column(ForeignKey("cuentas_por_pagar.id"), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    metodo: Mapped[str] = mapped_column(String(30), default="TRANSFERENCIA")
    referencia: Mapped[str | None] = mapped_column(String(100))
    fecha: Mapped[str | None] = mapped_column(String(10))


class Cobro(Base):
    __tablename__ = "cobros"

    id: Mapped[int] = mapped_column(primary_key=True)
    cuenta_cobrar_id: Mapped[int] = mapped_column(ForeignKey("cuentas_por_cobrar.id"), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    metodo: Mapped[str] = mapped_column(String(30), default="EFECTIVO")
    referencia: Mapped[str | None] = mapped_column(String(100))
    fecha: Mapped[str | None] = mapped_column(String(10))
