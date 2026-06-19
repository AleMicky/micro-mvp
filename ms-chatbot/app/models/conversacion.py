from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ChatbotConversacion(Base):
    __tablename__ = "chatbot_conversaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    sesion_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    canal: Mapped[str] = mapped_column(String(20), nullable=False, default="test")
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="menu")
    contexto: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    cliente_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
