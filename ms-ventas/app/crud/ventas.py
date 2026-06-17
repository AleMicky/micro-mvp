from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import (
    Cliente,
    CotizacionVenta,
    CotizacionVentaDetalle,
    Factura,
    FacturaDetalle,
    Venta,
    VentaDetalle,
)
from app.schemas.ventas import (
    ClienteCreate,
    ClienteUpdate,
    CotizacionVentaCreate,
    CotizacionVentaUpdate,
    VentaCreate,
    VentaUpdate,
)


def _calc(cantidad: Decimal, precio: Decimal) -> Decimal:
    return cantidad * precio


async def _next_codigo(db: AsyncSession, prefix: str, model) -> str:
    result = await db.execute(select(model.id).order_by(model.id.desc()).limit(1))
    last_id = result.scalar_one_or_none() or 0
    return f"{prefix}-{last_id + 1:05d}"


class CRUDCliente(CRUDBase[Cliente, ClienteCreate, ClienteUpdate]):
    pass


class CRUDCotizacionVenta:
    async def get(self, db: AsyncSession, id: int) -> CotizacionVenta | None:
        stmt = select(CotizacionVenta).where(CotizacionVenta.id == id).options(selectinload(CotizacionVenta.detalles))
        return (await db.execute(stmt)).scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[CotizacionVenta]:
        stmt = select(CotizacionVenta).options(selectinload(CotizacionVenta.detalles)).offset(skip).limit(limit).order_by(CotizacionVenta.id.desc())
        return list((await db.execute(stmt)).scalars().all())

    async def create(self, db: AsyncSession, payload: CotizacionVentaCreate) -> CotizacionVenta:
        codigo = await _next_codigo(db, "COT-V", CotizacionVenta)
        total = sum(_calc(d.cantidad, d.precio_unitario) for d in payload.detalles)
        obj = CotizacionVenta(codigo=codigo, cliente_id=payload.cliente_id, estado=payload.estado, fecha=payload.fecha, observaciones=payload.observaciones, total=total)
        db.add(obj)
        await db.flush()
        for d in payload.detalles:
            db.add(CotizacionVentaDetalle(cotizacion_id=obj.id, producto_id=d.producto_id, cantidad=d.cantidad, precio_unitario=d.precio_unitario, subtotal=_calc(d.cantidad, d.precio_unitario)))
        await db.commit()
        return await self.get(db, obj.id)  # type: ignore

    async def update(self, db: AsyncSession, obj: CotizacionVenta, payload: CotizacionVentaUpdate) -> CotizacionVenta:
        for field in ("cliente_id", "fecha", "observaciones", "estado", "activo"):
            val = getattr(payload, field)
            if val is not None:
                setattr(obj, field, val)
        if payload.detalles is not None:
            for det in list(obj.detalles):
                await db.delete(det)
            total = Decimal("0")
            for d in payload.detalles:
                sub = _calc(d.cantidad, d.precio_unitario)
                total += sub
                db.add(CotizacionVentaDetalle(cotizacion_id=obj.id, producto_id=d.producto_id, cantidad=d.cantidad, precio_unitario=d.precio_unitario, subtotal=sub))
            obj.total = total
        await db.commit()
        return await self.get(db, obj.id)  # type: ignore

    async def delete(self, db: AsyncSession, obj: CotizacionVenta) -> None:
        await db.delete(obj)
        await db.commit()


class CRUDVenta:
    async def get(self, db: AsyncSession, id: int) -> Venta | None:
        stmt = select(Venta).where(Venta.id == id).options(selectinload(Venta.detalles), selectinload(Venta.cliente))
        return (await db.execute(stmt)).scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Venta]:
        stmt = select(Venta).options(selectinload(Venta.detalles), selectinload(Venta.cliente)).offset(skip).limit(limit).order_by(Venta.id.desc())
        return list((await db.execute(stmt)).scalars().all())

    async def create(self, db: AsyncSession, payload: VentaCreate) -> Venta:
        codigo = await _next_codigo(db, "VTA", Venta)
        total = sum(_calc(d.cantidad, d.precio_unitario) for d in payload.detalles)
        obj = Venta(codigo=codigo, cliente_id=payload.cliente_id, cotizacion_id=payload.cotizacion_id, almacen_id=payload.almacen_id, estado=payload.estado, fecha=payload.fecha, observaciones=payload.observaciones, total=total)
        db.add(obj)
        await db.flush()
        for d in payload.detalles:
            db.add(VentaDetalle(venta_id=obj.id, producto_id=d.producto_id, cantidad=d.cantidad, precio_unitario=d.precio_unitario, subtotal=_calc(d.cantidad, d.precio_unitario)))
        await db.commit()
        return await self.get(db, obj.id)  # type: ignore

    async def update(self, db: AsyncSession, obj: Venta, payload: VentaUpdate) -> Venta:
        for field in ("cliente_id", "almacen_id", "fecha", "observaciones", "estado", "activo"):
            val = getattr(payload, field)
            if val is not None:
                setattr(obj, field, val)
        if payload.detalles is not None:
            for det in list(obj.detalles):
                await db.delete(det)
            total = Decimal("0")
            for d in payload.detalles:
                sub = _calc(d.cantidad, d.precio_unitario)
                total += sub
                db.add(VentaDetalle(venta_id=obj.id, producto_id=d.producto_id, cantidad=d.cantidad, precio_unitario=d.precio_unitario, subtotal=sub))
            obj.total = total
        await db.commit()
        return await self.get(db, obj.id)  # type: ignore

    async def delete(self, db: AsyncSession, obj: Venta) -> None:
        await db.delete(obj)
        await db.commit()


class CRUDFactura:
    async def get(self, db: AsyncSession, id: int) -> Factura | None:
        stmt = select(Factura).where(Factura.id == id).options(selectinload(Factura.detalles))
        return (await db.execute(stmt)).scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Factura]:
        stmt = select(Factura).options(selectinload(Factura.detalles)).offset(skip).limit(limit).order_by(Factura.id.desc())
        return list((await db.execute(stmt)).scalars().all())


crud_cliente = CRUDCliente(Cliente)
crud_cotizacion = CRUDCotizacionVenta()
crud_venta = CRUDVenta()
crud_factura = CRUDFactura()
