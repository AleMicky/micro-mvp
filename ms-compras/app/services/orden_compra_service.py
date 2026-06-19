from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.compras import crud_orden, _calc_subtotal, _next_codigo
from app.enums.estado import EstadoOrdenCompra
from app.models import OrdenCompra, OrdenCompraDetalle
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

    async def crear(self, db: AsyncSession, payload: OrdenCompraCreate):
        await proveedor_service.validar_activo(db, payload.proveedor_id)

        codigo = await _next_codigo(db, "OC", OrdenCompra)
        total = self._calcular_total(payload.detalles)

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
        self._agregar_detalles(db, orden.id, payload.detalles)
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
            orden.total = self._calcular_total(payload.detalles)
            self._agregar_detalles(db, orden.id, payload.detalles)

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
        if orden.estado == EstadoOrdenCompra.APROBADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cancelar una orden aprobada",
            )

        orden.estado = EstadoOrdenCompra.CANCELADA.value
        await db.commit()
        return await self.obtener(db, orden_id)

    @staticmethod
    def _calcular_total(detalles: list[OrdenCompraDetalleCreate]) -> Decimal:
        return sum(_calc_subtotal(d.cantidad, d.precio_unitario) for d in detalles)

    @staticmethod
    def _agregar_detalles(
        db: AsyncSession,
        orden_id: int,
        detalles: list[OrdenCompraDetalleCreate],
    ) -> None:
        for d in detalles:
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden_id,
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio_unitario=d.precio_unitario,
                    subtotal=_calc_subtotal(d.cantidad, d.precio_unitario),
                )
            )


orden_compra_service = OrdenCompraService()
