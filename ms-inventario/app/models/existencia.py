from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Existencia(Base, AuditoriaMixin):
    __tablename__ = "existencias"
    __table_args__ = (UniqueConstraint("producto_id", "almacen_id", name="uq_existencias_producto_almacen"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(nullable=False)
    almacen_id: Mapped[int] = mapped_column(ForeignKey("almacenes.id"), nullable=False)
    cantidad_actual: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0, nullable=False)
    stock_minimo: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0, nullable=False)
    stock_maximo: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))

    almacen: Mapped["Almacen"] = relationship(back_populates="existencias")
