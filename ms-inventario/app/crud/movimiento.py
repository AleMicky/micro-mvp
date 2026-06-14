from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movimiento_inventario import MovimientoInventario


class CRUDMovimiento:
    async def get_all(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        producto_id: int | None = None,
        almacen_id: int | None = None,
    ) -> list[MovimientoInventario]:
        stmt = select(MovimientoInventario).order_by(MovimientoInventario.creado_en.desc())
        if producto_id is not None:
            stmt = stmt.where(MovimientoInventario.producto_id == producto_id)
        if almacen_id is not None:
            stmt = stmt.where(MovimientoInventario.almacen_id == almacen_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_kardex(
        self,
        db: AsyncSession,
        *,
        producto_id: int,
        skip: int = 0,
        limit: int = 500,
    ) -> list[MovimientoInventario]:
        stmt = (
            select(MovimientoInventario)
            .where(MovimientoInventario.producto_id == producto_id)
            .order_by(MovimientoInventario.creado_en.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


crud_movimiento = CRUDMovimiento()
