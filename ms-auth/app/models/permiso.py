from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Permiso(AuditoriaMixin, Base):
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    roles: Mapped[list["Rol"]] = relationship(
        secondary="rol_permisos",
        back_populates="permisos",
        lazy="selectin",
    )


from app.models.rol import Rol  # noqa: E402
