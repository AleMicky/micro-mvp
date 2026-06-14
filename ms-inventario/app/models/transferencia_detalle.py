from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TransferenciaDetalle(Base):
    __tablename__ = "transferencia_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    transferencia_id: Mapped[int] = mapped_column(
        ForeignKey("transferencias_inventario.id", ondelete="CASCADE"), nullable=False
    )
    producto_id: Mapped[int] = mapped_column(nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    transferencia: Mapped["TransferenciaInventario"] = relationship(back_populates="detalles")
