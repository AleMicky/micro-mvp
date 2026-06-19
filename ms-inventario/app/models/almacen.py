from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Almacen(Base, AuditoriaMixin):
    __tablename__ = "almacenes"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[str | None] = mapped_column(Text)
    sucursal_id: Mapped[int | None] = mapped_column(Integer)

    existencias: Mapped[list["Existencia"]] = relationship(back_populates="almacen")
