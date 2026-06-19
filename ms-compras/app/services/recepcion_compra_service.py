from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.compras import crud_orden, crud_recepcion, _calc_subtotal, _next_codigo
from app.enums.estado import EstadoOrdenCompra, EstadoRecepcionCompra
from app.models import RecepcionCompra, RecepcionCompraDetalle
from app.schemas.compras import (
    RecepcionCompraCreate,
    RecepcionCompraDetalleCreate,
    RecepcionCompraUpdate,
)
from app.services.clients import inventario_client


class RecepcionCompraService:
    async def listar(self, db: AsyncSession, *, skip: int = 0, limit: int = 100):
        return await crud_recepcion.get_all(db, skip=skip, limit=limit)

    async def obtener(self, db: AsyncSession, recepcion_id: int):
        obj = await crud_recepcion.get(db, recepcion_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recepción de compra no encontrada")
        return obj

    def _validar_editable(self, recepcion: RecepcionCompra) -> None:
        if recepcion.estado in (
            EstadoRecepcionCompra.CONFIRMADA.value,
            EstadoRecepcionCompra.CANCELADA.value,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede modificar una recepción en estado {recepcion.estado}",
            )

    def _validar_eliminable(self, recepcion: RecepcionCompra) -> None:
        if recepcion.estado == EstadoRecepcionCompra.CONFIRMADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una recepción confirmada",
            )

    async def _validar_orden_aprobada(self, db: AsyncSession, orden_compra_id: int):
        orden = await crud_orden.get(db, orden_compra_id)
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden de compra {orden_compra_id} no encontrada",
            )
        if orden.estado != EstadoOrdenCompra.APROBADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden de compra debe estar APROBADA para crear una recepción",
            )
        return orden

    async def crear(self, db: AsyncSession, payload: RecepcionCompraCreate):
        await self._validar_orden_aprobada(db, payload.orden_compra_id)

        codigo = await _next_codigo(db, "REC", RecepcionCompra)
        total = self._calcular_total(payload.detalles)

        recepcion = RecepcionCompra(
            codigo=codigo,
            orden_id=payload.orden_compra_id,
            almacen_id=payload.almacen_id,
            estado=EstadoRecepcionCompra.BORRADOR.value,
            fecha=payload.fecha,
            observaciones=payload.observacion,
            total=total,
        )
        db.add(recepcion)
        await db.flush()
        self._agregar_detalles(db, recepcion.id, payload.detalles)
        await db.commit()
        return await self.obtener(db, recepcion.id)

    async def actualizar(self, db: AsyncSession, recepcion_id: int, payload: RecepcionCompraUpdate):
        recepcion = await self.obtener(db, recepcion_id)
        self._validar_editable(recepcion)

        if payload.almacen_id is not None:
            recepcion.almacen_id = payload.almacen_id
        if payload.fecha is not None:
            recepcion.fecha = payload.fecha
        if payload.observacion is not None:
            recepcion.observaciones = payload.observacion

        if payload.detalles is not None:
            for det in list(recepcion.detalles):
                await db.delete(det)
            recepcion.total = self._calcular_total(payload.detalles)
            self._agregar_detalles(db, recepcion.id, payload.detalles)

        await db.commit()
        return await self.obtener(db, recepcion_id)

    async def eliminar(self, db: AsyncSession, recepcion_id: int) -> None:
        recepcion = await self.obtener(db, recepcion_id)
        self._validar_eliminable(recepcion)
        await db.delete(recepcion)
        await db.commit()

    async def confirmar(self, db: AsyncSession, recepcion_id: int):
        recepcion = await self.obtener(db, recepcion_id)

        if recepcion.estado == EstadoRecepcionCompra.CANCELADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede confirmar una recepción cancelada",
            )
        if recepcion.estado == EstadoRecepcionCompra.CONFIRMADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La recepción ya está confirmada",
            )
        if recepcion.estado != EstadoRecepcionCompra.BORRADOR.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede confirmar una recepción en estado {recepcion.estado}",
            )

        for det in recepcion.detalles:
            await inventario_client.registrar_ingreso(
                producto_id=det.producto_id,
                almacen_id=recepcion.almacen_id,
                cantidad=det.cantidad_recibida,
                observacion="Ingreso por recepción de compra",
                referencia_tipo="RECEPCION_COMPRA",
                referencia_id=recepcion.id,
                creado_por="sistema",
            )

        recepcion.estado = EstadoRecepcionCompra.CONFIRMADA.value
        await db.commit()
        return await self.obtener(db, recepcion_id)

    async def cancelar(self, db: AsyncSession, recepcion_id: int):
        recepcion = await self.obtener(db, recepcion_id)

        if recepcion.estado == EstadoRecepcionCompra.CANCELADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La recepción ya está cancelada",
            )
        if recepcion.estado == EstadoRecepcionCompra.CONFIRMADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cancelar una recepción confirmada",
            )

        recepcion.estado = EstadoRecepcionCompra.CANCELADA.value
        await db.commit()
        return await self.obtener(db, recepcion_id)

    @staticmethod
    def _calcular_total(detalles: list[RecepcionCompraDetalleCreate]) -> Decimal:
        return sum(_calc_subtotal(d.cantidad_recibida, d.costo_unitario) for d in detalles)

    @staticmethod
    def _agregar_detalles(
        db: AsyncSession,
        recepcion_id: int,
        detalles: list[RecepcionCompraDetalleCreate],
    ) -> None:
        for d in detalles:
            db.add(
                RecepcionCompraDetalle(
                    recepcion_id=recepcion_id,
                    producto_id=d.producto_id,
                    cantidad_recibida=d.cantidad_recibida,
                    costo_unitario=d.costo_unitario,
                    subtotal=_calc_subtotal(d.cantidad_recibida, d.costo_unitario),
                )
            )


recepcion_compra_service = RecepcionCompraService()
