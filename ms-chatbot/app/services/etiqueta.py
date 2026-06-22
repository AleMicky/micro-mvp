from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.etiqueta import ChatbotEtiqueta
from app.schemas.etiqueta import EtiquetaCreate, EtiquetaUpdate


class EtiquetaService:
    async def listar(self, db: AsyncSession) -> list[ChatbotEtiqueta]:
        stmt = select(ChatbotEtiqueta).order_by(ChatbotEtiqueta.nombre.asc())
        return list((await db.execute(stmt)).scalars().all())

    async def get_by_id(self, db: AsyncSession, etiqueta_id: int) -> ChatbotEtiqueta | None:
        return await db.get(ChatbotEtiqueta, etiqueta_id)

    async def _get_by_nombre(self, db: AsyncSession, nombre: str) -> ChatbotEtiqueta | None:
        stmt = select(ChatbotEtiqueta).where(ChatbotEtiqueta.nombre == nombre)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def crear(self, db: AsyncSession, payload: EtiquetaCreate) -> ChatbotEtiqueta:
        existente = await self._get_by_nombre(db, payload.nombre)
        if existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una etiqueta con ese nombre")
        etiqueta = ChatbotEtiqueta(nombre=payload.nombre, color=payload.color)
        db.add(etiqueta)
        await db.commit()
        await db.refresh(etiqueta)
        return etiqueta

    async def actualizar(
        self, db: AsyncSession, etiqueta: ChatbotEtiqueta, payload: EtiquetaUpdate
    ) -> ChatbotEtiqueta:
        if payload.nombre is not None and payload.nombre != etiqueta.nombre:
            existente = await self._get_by_nombre(db, payload.nombre)
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Ya existe una etiqueta con ese nombre"
                )
            etiqueta.nombre = payload.nombre
        if payload.color is not None:
            etiqueta.color = payload.color
        await db.commit()
        await db.refresh(etiqueta)
        return etiqueta

    async def eliminar(self, db: AsyncSession, etiqueta: ChatbotEtiqueta) -> None:
        await db.delete(etiqueta)
        await db.commit()


etiqueta_service = EtiquetaService()
