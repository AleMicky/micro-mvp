from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Cliente(Base, AuditoriaMixin):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    rfc: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    telefono: Mapped[str | None] = mapped_column(String(30))
    direccion: Mapped[str | None] = mapped_column(Text)


class CotizacionVenta(Base, AuditoriaMixin):
    __tablename__ = "cotizaciones_venta"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="BORRADOR", nullable=False)
    fecha: Mapped[str | None] = mapped_column(String(10))
    observaciones: Mapped[str | None] = mapped_column(Text)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    cliente: Mapped["Cliente"] = relationship("Cliente")
    detalles: Mapped[list["CotizacionVentaDetalle"]] = relationship(
        "CotizacionVentaDetalle", back_populates="cotizacion", cascade="all, delete-orphan"
    )


class CotizacionVentaDetalle(Base):
    __tablename__ = "cotizacion_venta_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    cotizacion_id: Mapped[int] = mapped_column(ForeignKey("cotizaciones_venta.id", ondelete="CASCADE"))
    producto_id: Mapped[int] = mapped_column(nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    cotizacion: Mapped["CotizacionVenta"] = relationship("CotizacionVenta", back_populates="detalles")


class Venta(Base, AuditoriaMixin):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    cotizacion_id: Mapped[int | None] = mapped_column(ForeignKey("cotizaciones_venta.id"))
    almacen_id: Mapped[int] = mapped_column(nullable=False, default=1)
    estado: Mapped[str] = mapped_column(String(20), default="BORRADOR", nullable=False)
    fecha: Mapped[str | None] = mapped_column(String(10))
    observaciones: Mapped[str | None] = mapped_column(Text)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    cliente: Mapped["Cliente"] = relationship("Cliente")
    detalles: Mapped[list["VentaDetalle"]] = relationship(
        "VentaDetalle", back_populates="venta", cascade="all, delete-orphan"
    )


class VentaDetalle(Base):
    __tablename__ = "venta_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id", ondelete="CASCADE"))
    producto_id: Mapped[int] = mapped_column(nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    venta: Mapped["Venta"] = relationship("Venta", back_populates="detalles")


class Factura(Base, AuditoriaMixin):
    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="FACTURADA", nullable=False)
    fecha: Mapped[str | None] = mapped_column(String(10))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    impuesto: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    venta: Mapped["Venta"] = relationship("Venta")
    detalles: Mapped[list["FacturaDetalle"]] = relationship(
        "FacturaDetalle", back_populates="factura", cascade="all, delete-orphan"
    )


class FacturaDetalle(Base):
    __tablename__ = "factura_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas.id", ondelete="CASCADE"))
    producto_id: Mapped[int] = mapped_column(nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    factura: Mapped["Factura"] = relationship("Factura", back_populates="detalles")
