from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ChatbotMensaje(Base):
    __tablename__ = "chatbot_mensajes"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversacion_id: Mapped[int] = mapped_column(
        ForeignKey("chatbot_conversaciones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    direccion: Mapped[str] = mapped_column(String(10), nullable=False)
    origen: Mapped[str] = mapped_column(String(10), nullable=False, default="bot")
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_mensaje: Mapped[str] = mapped_column(String(10), nullable=False, default="texto")
    nombre_archivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wa_message_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
