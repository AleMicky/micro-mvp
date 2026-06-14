from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Producto(Base, AuditoriaMixin):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
    marca_id: Mapped[int | None] = mapped_column(ForeignKey("marcas.id"))
    unidad_medida_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_medida.id"), nullable=False
    )

    categoria: Mapped["Categoria"] = relationship(back_populates="productos")
    marca: Mapped["Marca | None"] = relationship(back_populates="productos")
    unidad_medida: Mapped["UnidadMedida"] = relationship(back_populates="productos")
