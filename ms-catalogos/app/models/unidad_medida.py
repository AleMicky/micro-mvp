from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class UnidadMedida(Base, AuditoriaMixin):
    __tablename__ = "unidades_medida"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    abreviatura: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    productos: Mapped[list["Producto"]] = relationship(back_populates="unidad_medida")
