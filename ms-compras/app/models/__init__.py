from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Proveedor(Base, AuditoriaMixin):
    __tablename__ = "proveedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    rfc: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    telefono: Mapped[str | None] = mapped_column(String(30))
    direccion: Mapped[str | None] = mapped_column(Text)


class CotizacionCompra(Base, AuditoriaMixin):
    __tablename__ = "cotizaciones_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="BORRADOR", nullable=False)
    fecha: Mapped[str | None] = mapped_column(String(10))
    observaciones: Mapped[str | None] = mapped_column(Text)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    proveedor: Mapped["Proveedor"] = relationship("Proveedor")
    detalles: Mapped[list["CotizacionCompraDetalle"]] = relationship(
        "CotizacionCompraDetalle", back_populates="cotizacion", cascade="all, delete-orphan"
    )


class CotizacionCompraDetalle(Base):
    __tablename__ = "cotizacion_compra_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    cotizacion_id: Mapped[int] = mapped_column(ForeignKey("cotizaciones_compra.id", ondelete="CASCADE"))
    producto_id: Mapped[int] = mapped_column(nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    cotizacion: Mapped["CotizacionCompra"] = relationship("CotizacionCompra", back_populates="detalles")


class OrdenCompra(Base, AuditoriaMixin):
    __tablename__ = "ordenes_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"), nullable=False)
    cotizacion_id: Mapped[int | None] = mapped_column(ForeignKey("cotizaciones_compra.id"))
    estado: Mapped[str] = mapped_column(String(20), default="BORRADOR", nullable=False)
    fecha: Mapped[str | None] = mapped_column(String(10))
    observaciones: Mapped[str | None] = mapped_column(Text)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    proveedor: Mapped["Proveedor"] = relationship("Proveedor")
    detalles: Mapped[list["OrdenCompraDetalle"]] = relationship(
        "OrdenCompraDetalle", back_populates="orden", cascade="all, delete-orphan"
    )


class OrdenCompraDetalle(Base):
    __tablename__ = "orden_compra_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes_compra.id", ondelete="CASCADE"))
    producto_id: Mapped[int] = mapped_column(nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    orden: Mapped["OrdenCompra"] = relationship("OrdenCompra", back_populates="detalles")


class RecepcionCompra(Base, AuditoriaMixin):
    __tablename__ = "recepciones_compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes_compra.id"), nullable=False)
    almacen_id: Mapped[int] = mapped_column(nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="BORRADOR", nullable=False)
    fecha: Mapped[str | None] = mapped_column(String(10))
    observaciones: Mapped[str | None] = mapped_column(Text)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    orden: Mapped["OrdenCompra"] = relationship("OrdenCompra")
    detalles: Mapped[list["RecepcionCompraDetalle"]] = relationship(
        "RecepcionCompraDetalle", back_populates="recepcion", cascade="all, delete-orphan"
    )


class RecepcionCompraDetalle(Base):
    __tablename__ = "recepcion_compra_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    recepcion_id: Mapped[int] = mapped_column(ForeignKey("recepciones_compra.id", ondelete="CASCADE"))
    producto_id: Mapped[int] = mapped_column(nullable=False)
    cantidad_recibida: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    costo_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    recepcion: Mapped["RecepcionCompra"] = relationship("RecepcionCompra", back_populates="detalles")
