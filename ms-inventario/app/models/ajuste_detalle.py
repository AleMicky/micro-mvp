from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AjusteDetalle(Base):
    __tablename__ = "ajuste_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    ajuste_id: Mapped[int] = mapped_column(
        ForeignKey("ajustes_inventario.id", ondelete="CASCADE"), nullable=False
    )
    producto_id: Mapped[int] = mapped_column(nullable=False)
    cantidad_anterior: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    cantidad_nueva: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    diferencia: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ajuste: Mapped["AjusteInventario"] = relationship(back_populates="detalles")
