from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import (
    CotizacionCompra,
    CotizacionCompraDetalle,
    OrdenCompra,
    Proveedor,
    RecepcionCompra,
)
from app.schemas.compras import (
    CotizacionCompraCreate,
    CotizacionCompraUpdate,
    ProveedorCreate,
    ProveedorUpdate,
)


def _calc_subtotal(cantidad: Decimal, precio: Decimal) -> Decimal:
    return cantidad * precio


async def _next_codigo(db: AsyncSession, prefix: str, model) -> str:
    result = await db.execute(select(model.id).order_by(model.id.desc()).limit(1))
    last_id = result.scalar_one_or_none() or 0
    return f"{prefix}-{last_id + 1:05d}"


class CRUDProveedor(CRUDBase[Proveedor, ProveedorCreate, ProveedorUpdate]):
    pass


class CRUDCotizacion:
    async def get(self, db: AsyncSession, id: int) -> CotizacionCompra | None:
        stmt = (
            select(CotizacionCompra)
            .where(CotizacionCompra.id == id)
            .options(selectinload(CotizacionCompra.detalles))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[CotizacionCompra]:
        stmt = (
            select(CotizacionCompra)
            .options(selectinload(CotizacionCompra.detalles))
            .offset(skip)
            .limit(limit)
            .order_by(CotizacionCompra.id.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, payload: CotizacionCompraCreate) -> CotizacionCompra:
        codigo = await _next_codigo(db, "COT", CotizacionCompra)
        total = sum(_calc_subtotal(d.cantidad, d.precio_unitario) for d in payload.detalles)
        cot = CotizacionCompra(
            codigo=codigo,
            proveedor_id=payload.proveedor_id,
            estado=payload.estado,
            fecha=payload.fecha,
            observaciones=payload.observaciones,
            total=total,
        )
        db.add(cot)
        await db.flush()
        for d in payload.detalles:
            db.add(
                CotizacionCompraDetalle(
                    cotizacion_id=cot.id,
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio_unitario=d.precio_unitario,
                    subtotal=_calc_subtotal(d.cantidad, d.precio_unitario),
                )
            )
        await db.commit()
        return await self.get(db, cot.id)  # type: ignore

    async def update(self, db: AsyncSession, cot: CotizacionCompra, payload: CotizacionCompraUpdate) -> CotizacionCompra:
        for field in ("proveedor_id", "fecha", "observaciones", "estado", "activo"):
            val = getattr(payload, field)
            if val is not None:
                setattr(cot, field, val)
        if payload.detalles is not None:
            for det in list(cot.detalles):
                await db.delete(det)
            total = Decimal("0")
            for d in payload.detalles:
                sub = _calc_subtotal(d.cantidad, d.precio_unitario)
                total += sub
                db.add(
                    CotizacionCompraDetalle(
                        cotizacion_id=cot.id,
                        producto_id=d.producto_id,
                        cantidad=d.cantidad,
                        precio_unitario=d.precio_unitario,
                        subtotal=sub,
                    )
                )
            cot.total = total
        await db.commit()
        return await self.get(db, cot.id)  # type: ignore

    async def delete(self, db: AsyncSession, cot: CotizacionCompra) -> None:
        await db.delete(cot)
        await db.commit()


class CRUDOrden:
    async def get(self, db: AsyncSession, id: int) -> OrdenCompra | None:
        stmt = (
            select(OrdenCompra)
            .where(OrdenCompra.id == id)
            .options(selectinload(OrdenCompra.detalles), selectinload(OrdenCompra.proveedor))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[OrdenCompra]:
        stmt = (
            select(OrdenCompra)
            .options(selectinload(OrdenCompra.detalles), selectinload(OrdenCompra.proveedor))
            .offset(skip)
            .limit(limit)
            .order_by(OrdenCompra.id.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


class CRUDRecepcion:
    async def get(self, db: AsyncSession, id: int) -> RecepcionCompra | None:
        stmt = (
            select(RecepcionCompra)
            .where(RecepcionCompra.id == id)
            .options(
                selectinload(RecepcionCompra.detalles),
                selectinload(RecepcionCompra.orden),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[RecepcionCompra]:
        stmt = (
            select(RecepcionCompra)
            .options(
                selectinload(RecepcionCompra.detalles),
                selectinload(RecepcionCompra.orden),
            )
            .offset(skip)
            .limit(limit)
            .order_by(RecepcionCompra.id.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


crud_proveedor = CRUDProveedor(Proveedor)
crud_cotizacion = CRUDCotizacion()
crud_orden = CRUDOrden()
crud_recepcion = CRUDRecepcion()
