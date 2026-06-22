from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversacion_etiqueta import ChatbotConversacionEtiqueta
from app.models.etiqueta import ChatbotEtiqueta


class ConversacionEtiquetaService:
    async def listar_por_conversacion(self, db: AsyncSession, conversacion_id: int) -> list[ChatbotEtiqueta]:
        stmt = (
            select(ChatbotEtiqueta)
            .join(ChatbotConversacionEtiqueta, ChatbotConversacionEtiqueta.etiqueta_id == ChatbotEtiqueta.id)
            .where(ChatbotConversacionEtiqueta.conversacion_id == conversacion_id)
            .order_by(ChatbotEtiqueta.nombre.asc())
        )
        return list((await db.execute(stmt)).scalars().all())

    async def listar_por_conversaciones(
        self, db: AsyncSession, conversacion_ids: list[int]
    ) -> dict[int, list[ChatbotEtiqueta]]:
        if not conversacion_ids:
            return {}
        stmt = (
            select(ChatbotConversacionEtiqueta.conversacion_id, ChatbotEtiqueta)
            .join(ChatbotEtiqueta, ChatbotEtiqueta.id == ChatbotConversacionEtiqueta.etiqueta_id)
            .where(ChatbotConversacionEtiqueta.conversacion_id.in_(conversacion_ids))
            .order_by(ChatbotEtiqueta.nombre.asc())
        )
        resultado: dict[int, list[ChatbotEtiqueta]] = {cid: [] for cid in conversacion_ids}
        for conversacion_id, etiqueta in (await db.execute(stmt)).all():
            resultado[conversacion_id].append(etiqueta)
        return resultado

    async def existe_asignacion(self, db: AsyncSession, conversacion_id: int, etiqueta_id: int) -> bool:
        stmt = select(ChatbotConversacionEtiqueta).where(
            ChatbotConversacionEtiqueta.conversacion_id == conversacion_id,
            ChatbotConversacionEtiqueta.etiqueta_id == etiqueta_id,
        )
        return (await db.execute(stmt)).scalar_one_or_none() is not None

    async def asignar(self, db: AsyncSession, conversacion_id: int, etiqueta_id: int) -> None:
        if await self.existe_asignacion(db, conversacion_id, etiqueta_id):
            return
        db.add(ChatbotConversacionEtiqueta(conversacion_id=conversacion_id, etiqueta_id=etiqueta_id))
        await db.commit()

    async def desasignar(self, db: AsyncSession, conversacion_id: int, etiqueta_id: int) -> None:
        stmt = delete(ChatbotConversacionEtiqueta).where(
            ChatbotConversacionEtiqueta.conversacion_id == conversacion_id,
            ChatbotConversacionEtiqueta.etiqueta_id == etiqueta_id,
        )
        await db.execute(stmt)
        await db.commit()


conversacion_etiqueta_service = ConversacionEtiquetaService()
