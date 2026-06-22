from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mensaje import ChatbotMensaje


class MensajeService:
    async def existe_por_wa_id(self, db: AsyncSession, wa_message_id: str) -> bool:
        stmt = select(ChatbotMensaje.id).where(ChatbotMensaje.wa_message_id == wa_message_id)
        return (await db.execute(stmt)).scalar_one_or_none() is not None

    async def crear(
        self,
        db: AsyncSession,
        conversacion_id: int,
        direccion: str,
        texto: str,
        wa_message_id: str | None = None,
        origen: str = "bot",
        tipo_mensaje: str = "texto",
        nombre_archivo: str | None = None,
    ) -> ChatbotMensaje:
        mensaje = ChatbotMensaje(
            conversacion_id=conversacion_id,
            direccion=direccion,
            texto=texto,
            wa_message_id=wa_message_id,
            origen=origen,
            tipo_mensaje=tipo_mensaje,
            nombre_archivo=nombre_archivo,
        )
        db.add(mensaje)
        await db.commit()
        await db.refresh(mensaje)
        return mensaje

    async def listar_por_conversacion(self, db: AsyncSession, conversacion_id: int) -> list[ChatbotMensaje]:
        stmt = (
            select(ChatbotMensaje)
            .where(ChatbotMensaje.conversacion_id == conversacion_id)
            .order_by(ChatbotMensaje.creado_en.asc())
        )
        return list((await db.execute(stmt)).scalars().all())

    async def ultimo_por_conversacion(self, db: AsyncSession, conversacion_id: int) -> ChatbotMensaje | None:
        stmt = (
            select(ChatbotMensaje)
            .where(ChatbotMensaje.conversacion_id == conversacion_id)
            .order_by(ChatbotMensaje.creado_en.desc())
            .limit(1)
        )
        return (await db.execute(stmt)).scalar_one_or_none()


mensaje_service = MensajeService()
