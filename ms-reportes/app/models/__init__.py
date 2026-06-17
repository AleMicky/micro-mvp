from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReporteGenerado(Base):
    __tablename__ = "reportes_generados"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    parametros: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Exportacion(Base):
    __tablename__ = "exportaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_reporte: Mapped[str] = mapped_column(String(50), nullable=False)
    formato: Mapped[str] = mapped_column(String(10), nullable=False)
    archivo: Mapped[str | None] = mapped_column(String(255))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
