from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    producto_id: Mapped[int] = mapped_column(nullable=False)
    almacen_id: Mapped[int] = mapped_column(ForeignKey("almacenes.id"), nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    cantidad_anterior: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    cantidad_nueva: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    referencia_tipo: Mapped[str | None] = mapped_column(String(50))
    referencia_id: Mapped[int | None] = mapped_column()
    observaciones: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
