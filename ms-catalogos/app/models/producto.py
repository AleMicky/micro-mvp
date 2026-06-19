from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Producto(Base, AuditoriaMixin):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    codigo_barras: Mapped[str | None] = mapped_column(String(50))
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
    marca_id: Mapped[int | None] = mapped_column(ForeignKey("marcas.id"))
    unidad_medida_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_medida.id"), nullable=False
    )
    precio_base: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVO")

    categoria: Mapped["Categoria"] = relationship(back_populates="productos")
    marca: Mapped["Marca | None"] = relationship(back_populates="productos")
    unidad_medida: Mapped["UnidadMedida"] = relationship(back_populates="productos")
