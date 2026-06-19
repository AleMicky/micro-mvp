from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.compras import crud_proveedor
from app.schemas.compras import ProveedorCreate, ProveedorUpdate


class ProveedorService:
    async def listar(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        solo_activos: bool = False,
    ):
        return await crud_proveedor.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)

    async def obtener(self, db: AsyncSession, proveedor_id: int):
        obj = await crud_proveedor.get(db, proveedor_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
        return obj

    async def crear(self, db: AsyncSession, payload: ProveedorCreate):
        obj = await crud_proveedor.create(db, payload)
        await db.commit()
        return obj

    async def actualizar(self, db: AsyncSession, proveedor_id: int, payload: ProveedorUpdate):
        obj = await self.obtener(db, proveedor_id)
        obj = await crud_proveedor.update(db, obj, payload)
        await db.commit()
        return obj

    async def eliminar(self, db: AsyncSession, proveedor_id: int) -> None:
        obj = await self.obtener(db, proveedor_id)
        obj.activo = False
        await db.commit()

    async def validar_activo(self, db: AsyncSession, proveedor_id: int):
        proveedor = await self.obtener(db, proveedor_id)
        if not proveedor.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El proveedor {proveedor_id} no está activo",
            )
        return proveedor


proveedor_service = ProveedorService()
