from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.catalogos_client import catalogos_client
from app.crud.compras import crud_orden, _calc_subtotal, _next_codigo
from app.enums.estado import EstadoOrdenCompra, EstadoRecepcionCompra
from app.models import OrdenCompra, OrdenCompraDetalle, RecepcionCompra
from app.schemas.compras import OrdenCompraCreate, OrdenCompraDetalleCreate, OrdenCompraUpdate
from app.services.proveedor_service import proveedor_service


class OrdenCompraService:
    async def listar(self, db: AsyncSession, *, skip: int = 0, limit: int = 100):
        return await crud_orden.get_all(db, skip=skip, limit=limit)

    async def obtener(self, db: AsyncSession, orden_id: int):
        obj = await crud_orden.get(db, orden_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        return obj

    def _validar_editable(self, orden: OrdenCompra) -> None:
        if orden.estado in (EstadoOrdenCompra.APROBADA.value, EstadoOrdenCompra.CANCELADA.value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede modificar una orden en estado {orden.estado}",
            )

    def _validar_eliminable(self, orden: OrdenCompra) -> None:
        if orden.estado == EstadoOrdenCompra.APROBADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una orden aprobada",
            )

    async def _tiene_recepciones_confirmadas(self, db: AsyncSession, orden_id: int) -> bool:
        stmt = select(RecepcionCompra.id).where(
            RecepcionCompra.orden_id == orden_id,
            RecepcionCompra.estado == EstadoRecepcionCompra.CONFIRMADA.value,
        )
        return (await db.execute(stmt)).scalar_one_or_none() is not None

    async def crear(self, db: AsyncSession, payload: OrdenCompraCreate):
        await proveedor_service.validar_activo(db, payload.proveedor_id)

        codigo = await _next_codigo(db, "OC", OrdenCompra)
        total = await self._calcular_total(payload.detalles)

        orden = OrdenCompra(
            codigo=codigo,
            proveedor_id=payload.proveedor_id,
            cotizacion_id=payload.cotizacion_id,
            estado=EstadoOrdenCompra.BORRADOR.value,
            fecha=payload.fecha,
            observaciones=payload.observacion,
            total=total,
        )
        db.add(orden)
        await db.flush()
        await self._agregar_detalles(db, orden.id, payload.detalles)
        await db.commit()
        return await self.obtener(db, orden.id)

    async def actualizar(self, db: AsyncSession, orden_id: int, payload: OrdenCompraUpdate):
        orden = await self.obtener(db, orden_id)
        self._validar_editable(orden)

        if payload.proveedor_id is not None:
            await proveedor_service.validar_activo(db, payload.proveedor_id)
            orden.proveedor_id = payload.proveedor_id

        if payload.cotizacion_id is not None:
            orden.cotizacion_id = payload.cotizacion_id
        if payload.fecha is not None:
            orden.fecha = payload.fecha
        if payload.observacion is not None:
            orden.observaciones = payload.observacion

        if payload.detalles is not None:
            for det in list(orden.detalles):
                await db.delete(det)
            orden.total = await self._calcular_total(payload.detalles)
            await self._agregar_detalles(db, orden.id, payload.detalles)

        await db.commit()
        return await self.obtener(db, orden_id)

    async def eliminar(self, db: AsyncSession, orden_id: int) -> None:
        orden = await self.obtener(db, orden_id)
        self._validar_eliminable(orden)
        await db.delete(orden)
        await db.commit()

    async def aprobar(self, db: AsyncSession, orden_id: int):
        orden = await self.obtener(db, orden_id)

        if orden.estado == EstadoOrdenCompra.CANCELADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede aprobar una orden cancelada",
            )
        if orden.estado == EstadoOrdenCompra.APROBADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden ya está aprobada",
            )
        if orden.estado != EstadoOrdenCompra.BORRADOR.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede aprobar una orden en estado {orden.estado}",
            )

        orden.estado = EstadoOrdenCompra.APROBADA.value
        await db.commit()
        return await self.obtener(db, orden_id)

    async def cancelar(self, db: AsyncSession, orden_id: int):
        orden = await self.obtener(db, orden_id)

        if orden.estado == EstadoOrdenCompra.CANCELADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden ya está cancelada",
            )
        if await self._tiene_recepciones_confirmadas(db, orden_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cancelar una orden con recepciones confirmadas",
            )

        orden.estado = EstadoOrdenCompra.CANCELADA.value
        await db.commit()
        return await self.obtener(db, orden_id)

    async def _calcular_total(self, detalles: list[OrdenCompraDetalleCreate]) -> Decimal:
        total = Decimal("0")
        for d in detalles:
            await catalogos_client.obtener_producto_por_id(d.producto_id)
            total += _calc_subtotal(d.cantidad, d.precio_unitario)
        return total

    async def _agregar_detalles(
        self,
        db: AsyncSession,
        orden_id: int,
        detalles: list[OrdenCompraDetalleCreate],
    ) -> None:
        for d in detalles:
            producto = await catalogos_client.obtener_producto_por_id(d.producto_id)
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden_id,
                    producto_id=d.producto_id,
                    producto_codigo=producto.get("codigo"),
                    producto_nombre=producto.get("nombre"),
                    cantidad=d.cantidad,
                    precio_unitario=d.precio_unitario,
                    subtotal=_calc_subtotal(d.cantidad, d.precio_unitario),
                )
            )


orden_compra_service = OrdenCompraService()
