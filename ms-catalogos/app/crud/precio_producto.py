from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.precio_producto import PrecioProducto
from app.schemas.precio_producto import PrecioProductoCreate


class CRUDPrecioProducto:
    async def get_activo(self, db: AsyncSession, producto_id: int) -> PrecioProducto | None:
        stmt = (
            select(PrecioProducto)
            .where(PrecioProducto.producto_id == producto_id, PrecioProducto.activo.is_(True))
            .limit(1)
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    async def get_activos_map(
        self, db: AsyncSession, producto_ids: list[int]
    ) -> dict[int, PrecioProducto]:
        if not producto_ids:
            return {}
        stmt = select(PrecioProducto).where(
            PrecioProducto.producto_id.in_(producto_ids),
            PrecioProducto.activo.is_(True),
        )
        rows = (await db.execute(stmt)).scalars().all()
        return {row.producto_id: row for row in rows}

    async def get_historial(self, db: AsyncSession, producto_id: int) -> list[PrecioProducto]:
        stmt = (
            select(PrecioProducto)
            .where(PrecioProducto.producto_id == producto_id)
            .order_by(PrecioProducto.fecha_inicio.desc())
        )
        return list((await db.execute(stmt)).scalars().all())

    async def crear_precio(
        self, db: AsyncSession, producto_id: int, obj_in: PrecioProductoCreate
    ) -> PrecioProducto:
        now = datetime.now(timezone.utc)
        await db.execute(
            update(PrecioProducto)
            .where(
                PrecioProducto.producto_id == producto_id,
                PrecioProducto.activo.is_(True),
            )
            .values(activo=False, fecha_fin=now)
        )
        precio = PrecioProducto(
            producto_id=producto_id,
            precio_venta=obj_in.precio_venta,
            fecha_inicio=now,
            activo=True,
        )
        db.add(precio)
        await db.commit()
        await db.refresh(precio)
        return precio

    async def crear_precio_inicial(
        self, db: AsyncSession, producto_id: int, precio_venta: Decimal
    ) -> PrecioProducto:
        return await self.crear_precio(
            db, producto_id, PrecioProductoCreate(precio_venta=precio_venta)
        )


crud_precio_producto = CRUDPrecioProducto()
