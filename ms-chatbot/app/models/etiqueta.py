from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ChatbotEtiqueta(Base):
    __tablename__ = "chatbot_etiquetas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#64748b")
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
