from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class AjusteInventario(Base, AuditoriaMixin):
    __tablename__ = "ajustes_inventario"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str | None] = mapped_column(String(50))
    almacen_id: Mapped[int] = mapped_column(ForeignKey("almacenes.id"), nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text)
    observaciones: Mapped[str | None] = mapped_column(Text)

    detalles: Mapped[list["AjusteDetalle"]] = relationship(
        back_populates="ajuste", cascade="all, delete-orphan"
    )
