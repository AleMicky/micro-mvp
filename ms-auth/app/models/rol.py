from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditoriaMixin


class Rol(AuditoriaMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    usuarios: Mapped[list["Usuario"]] = relationship(
        secondary="usuario_roles",
        back_populates="roles",
        lazy="selectin",
    )
    permisos: Mapped[list["Permiso"]] = relationship(
        secondary="rol_permisos",
        back_populates="roles",
        lazy="selectin",
    )


from app.models.permiso import Permiso  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402
