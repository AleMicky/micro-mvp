from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class TransferenciaInventario(Base, AuditoriaMixin):
    __tablename__ = "transferencias_inventario"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str | None] = mapped_column(String(50))
    almacen_origen_id: Mapped[int] = mapped_column(ForeignKey("almacenes.id"), nullable=False)
    almacen_destino_id: Mapped[int] = mapped_column(ForeignKey("almacenes.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default="COMPLETADA", nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text)

    detalles: Mapped[list["TransferenciaDetalle"]] = relationship(
        back_populates="transferencia", cascade="all, delete-orphan"
    )
