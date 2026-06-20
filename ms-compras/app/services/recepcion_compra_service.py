from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.catalogos_client import catalogos_client
from app.clients.inventario_client import inventario_client
from app.crud.compras import crud_orden, crud_recepcion, _calc_subtotal, _next_codigo
from app.enums.estado import EstadoOrdenCompra, EstadoRecepcionCompra
from app.models import RecepcionCompra, RecepcionCompraDetalle
from app.schemas.compras import (
    RecepcionCompraCreate,
    RecepcionCompraDetalleCreate,
    RecepcionCompraUpdate,
)


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

    async def _aplicar_snapshot_almacen(self, recepcion: RecepcionCompra, almacen_id: int) -> None:
        almacen = await inventario_client.obtener_almacen_por_id(almacen_id)
        recepcion.almacen_id = almacen_id
        recepcion.almacen_nombre = almacen.get("nombre")
        recepcion.sucursal_id = almacen.get("sucursal_id")
        recepcion.sucursal_nombre = almacen.get("sucursal_nombre")
        recepcion.compania_id = almacen.get("compania_id")
        recepcion.compania_nombre = almacen.get("compania_nombre")

    async def crear(self, db: AsyncSession, payload: RecepcionCompraCreate):
        await self._validar_orden_aprobada(db, payload.orden_compra_id)
        almacen = await inventario_client.obtener_almacen_por_id(payload.almacen_id)

        codigo = await _next_codigo(db, "REC", RecepcionCompra)
        total = await self._calcular_total(payload.detalles)

        recepcion = RecepcionCompra(
            codigo=codigo,
            orden_id=payload.orden_compra_id,
            almacen_id=payload.almacen_id,
            almacen_nombre=almacen.get("nombre"),
            sucursal_id=almacen.get("sucursal_id"),
            sucursal_nombre=almacen.get("sucursal_nombre"),
            compania_id=almacen.get("compania_id"),
            compania_nombre=almacen.get("compania_nombre"),
            estado=EstadoRecepcionCompra.BORRADOR.value,
            fecha=payload.fecha,
            observaciones=payload.observacion,
            total=total,
        )
        db.add(recepcion)
        await db.flush()
        await self._agregar_detalles(db, recepcion.id, payload.detalles)
        await db.commit()
        return await self.obtener(db, recepcion.id)

    async def actualizar(self, db: AsyncSession, recepcion_id: int, payload: RecepcionCompraUpdate):
        recepcion = await self.obtener(db, recepcion_id)
        self._validar_editable(recepcion)

        if payload.almacen_id is not None:
            await self._aplicar_snapshot_almacen(recepcion, payload.almacen_id)
        if payload.fecha is not None:
            recepcion.fecha = payload.fecha
        if payload.observacion is not None:
            recepcion.observaciones = payload.observacion

        if payload.detalles is not None:
            for det in list(recepcion.detalles):
                await db.delete(det)
            recepcion.total = await self._calcular_total(payload.detalles)
            await self._agregar_detalles(db, recepcion.id, payload.detalles)

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
                costo_unitario=det.costo_unitario,
                observacion=f"Ingreso por recepción {recepcion.codigo}",
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

    async def _calcular_total(self, detalles: list[RecepcionCompraDetalleCreate]) -> Decimal:
        total = Decimal("0")
        for d in detalles:
            await catalogos_client.obtener_producto_por_id(d.producto_id)
            total += _calc_subtotal(d.cantidad_recibida, d.costo_unitario)
        return total

    async def _agregar_detalles(
        self,
        db: AsyncSession,
        recepcion_id: int,
        detalles: list[RecepcionCompraDetalleCreate],
    ) -> None:
        for d in detalles:
            producto = await catalogos_client.obtener_producto_por_id(d.producto_id)
            db.add(
                RecepcionCompraDetalle(
                    recepcion_id=recepcion_id,
                    producto_id=d.producto_id,
                    producto_codigo=producto.get("codigo"),
                    producto_nombre=producto.get("nombre"),
                    cantidad_recibida=d.cantidad_recibida,
                    costo_unitario=d.costo_unitario,
                    subtotal=_calc_subtotal(d.cantidad_recibida, d.costo_unitario),
                )
            )


recepcion_compra_service = RecepcionCompraService()
