from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ChatbotConversacionEtiqueta(Base):
    __tablename__ = "chatbot_conversacion_etiquetas"

    conversacion_id: Mapped[int] = mapped_column(
        ForeignKey("chatbot_conversaciones.id", ondelete="CASCADE"), primary_key=True
    )
    etiqueta_id: Mapped[int] = mapped_column(
        ForeignKey("chatbot_etiquetas.id", ondelete="CASCADE"), primary_key=True
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
