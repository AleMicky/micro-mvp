from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Sucursal(Base, AuditoriaMixin):
    __tablename__ = "sucursales"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    compania_id: Mapped[int] = mapped_column(ForeignKey("companias.id"), nullable=False)
    ciudad_id: Mapped[int] = mapped_column(ForeignKey("ciudades.id"), nullable=False)
    direccion: Mapped[str | None] = mapped_column(Text)

    compania: Mapped["Compania"] = relationship(back_populates="sucursales")
    ciudad: Mapped["Ciudad"] = relationship(back_populates="sucursales")
