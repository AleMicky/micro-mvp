from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.existencia import Existencia


class CRUDExistencia:
    async def get(self, db: AsyncSession, id: int) -> Existencia | None:
        return await db.get(Existencia, id)

    async def get_by_producto_almacen(
        self,
        db: AsyncSession,
        *,
        producto_id: int,
        almacen_id: int,
    ) -> Existencia | None:
        stmt = select(Existencia).where(
            Existencia.producto_id == producto_id,
            Existencia.almacen_id == almacen_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        producto_id: int | None = None,
        almacen_id: int | None = None,
    ) -> list[Existencia]:
        stmt = select(Existencia)
        if producto_id is not None:
            stmt = stmt.where(Existencia.producto_id == producto_id)
        if almacen_id is not None:
            stmt = stmt.where(Existencia.almacen_id == almacen_id)
        stmt = stmt.order_by(Existencia.actualizado_en.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        *,
        producto_id: int,
        almacen_id: int,
        cantidad_actual: Decimal = Decimal("0"),
        stock_minimo: Decimal = Decimal("0"),
        stock_maximo: Decimal | None = None,
    ) -> Existencia:
        existencia = Existencia(
            producto_id=producto_id,
            almacen_id=almacen_id,
            cantidad_actual=cantidad_actual,
            stock_minimo=stock_minimo,
            stock_maximo=stock_maximo,
        )
        db.add(existencia)
        await db.flush()
        return existencia


crud_existencia = CRUDExistencia()
