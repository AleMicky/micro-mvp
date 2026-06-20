from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.compras import crud_proveedor
from app.models import Proveedor
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

    async def _validar_unico(
        self,
        db: AsyncSession,
        *,
        codigo: str,
        rfc: str | None,
        exclude_id: int | None = None,
    ) -> None:
        condiciones = [Proveedor.codigo == codigo]
        if rfc:
            condiciones.append(Proveedor.rfc == rfc)
        stmt = select(Proveedor).where(or_(*condiciones))
        if exclude_id is not None:
            stmt = stmt.where(Proveedor.id != exclude_id)
        existente = (await db.execute(stmt)).scalar_one_or_none()
        if existente:
            if existente.codigo == codigo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un proveedor con código {codigo}",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un proveedor con NIT/RFC {rfc}",
            )

    async def crear(self, db: AsyncSession, payload: ProveedorCreate):
        await self._validar_unico(db, codigo=payload.codigo, rfc=payload.rfc)
        obj = await crud_proveedor.create(db, payload)
        await db.commit()
        return obj

    async def actualizar(self, db: AsyncSession, proveedor_id: int, payload: ProveedorUpdate):
        obj = await self.obtener(db, proveedor_id)
        codigo = payload.codigo if payload.codigo is not None else obj.codigo
        rfc = payload.rfc if payload.rfc is not None else obj.rfc
        await self._validar_unico(db, codigo=codigo, rfc=rfc, exclude_id=proveedor_id)
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
