from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Ciudad(Base, AuditoriaMixin):
    __tablename__ = "ciudades"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    departamento: Mapped[str | None] = mapped_column(String(150))

    sucursales: Mapped[list["Sucursal"]] = relationship(back_populates="ciudad")
