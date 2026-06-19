from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversacion import ChatbotConversacion


class ConversacionService:
    async def get_by_sesion(self, db: AsyncSession, sesion_id: str) -> ChatbotConversacion | None:
        stmt = select(ChatbotConversacion).where(ChatbotConversacion.sesion_id == sesion_id)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def get_or_create(self, db: AsyncSession, sesion_id: str) -> ChatbotConversacion:
        conversacion = await self.get_by_sesion(db, sesion_id)
        if conversacion:
            return conversacion

        conversacion = ChatbotConversacion(sesion_id=sesion_id, estado="menu", contexto={})
        db.add(conversacion)
        await db.commit()
        await db.refresh(conversacion)
        return conversacion

    async def actualizar_estado(
        self,
        db: AsyncSession,
        conversacion: ChatbotConversacion,
        nuevo_estado: str,
        nuevo_contexto: dict,
    ) -> ChatbotConversacion:
        conversacion.estado = nuevo_estado
        conversacion.contexto = nuevo_contexto
        await db.commit()
        await db.refresh(conversacion)
        return conversacion

    async def get_or_create_whatsapp(self, db: AsyncSession, numero: str) -> ChatbotConversacion:
        conversacion = await self.get_by_sesion(db, numero)
        if conversacion:
            return conversacion

        conversacion = ChatbotConversacion(sesion_id=numero, estado="menu", contexto={}, canal="whatsapp")
        db.add(conversacion)
        await db.commit()
        await db.refresh(conversacion)
        return conversacion

    async def listar(self, db: AsyncSession, canal: str | None = None) -> list[ChatbotConversacion]:
        stmt = select(ChatbotConversacion)
        if canal:
            stmt = stmt.where(ChatbotConversacion.canal == canal)
        stmt = stmt.order_by(ChatbotConversacion.actualizado_en.desc())
        return list((await db.execute(stmt)).scalars().all())

    async def get_by_id(self, db: AsyncSession, conversacion_id: int) -> ChatbotConversacion | None:
        return await db.get(ChatbotConversacion, conversacion_id)


conversacion_service = ConversacionService()
