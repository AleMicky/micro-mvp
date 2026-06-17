from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.compras import crud_orden, crud_recepcion, _next_codigo
from app.enums.estado import EstadoDocumento
from app.models import RecepcionCompra, RecepcionCompraDetalle
from app.schemas.compras import RecepcionCompraCreate
from app.services.clients import finanzas_client, inventario_client


class CompraService:
    async def aprobar_orden(self, db: AsyncSession, orden_id: int):
        orden = await crud_orden.get(db, orden_id)
        if not orden:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada")
        if orden.estado not in (EstadoDocumento.BORRADOR.value, EstadoDocumento.PENDIENTE.value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede aprobar orden en estado {orden.estado}",
            )
        orden.estado = EstadoDocumento.APROBADA.value
        await db.commit()
        return await crud_orden.get(db, orden_id)

    async def registrar_recepcion(self, db: AsyncSession, payload: RecepcionCompraCreate):
        orden = await crud_orden.get(db, payload.orden_id)
        if not orden:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada")
        if orden.estado != EstadoDocumento.APROBADA.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden debe estar APROBADA para recepcionar",
            )

        codigo = await _next_codigo(db, "REC", RecepcionCompra)
        recepcion = RecepcionCompra(
            codigo=codigo,
            orden_id=payload.orden_id,
            almacen_id=payload.almacen_id,
            estado=EstadoDocumento.RECIBIDA.value,
            fecha=payload.fecha,
            observaciones=payload.observaciones,
        )
        db.add(recepcion)
        await db.flush()

        for det in payload.detalles:
            db.add(
                RecepcionCompraDetalle(
                    recepcion_id=recepcion.id,
                    producto_id=det.producto_id,
                    cantidad=det.cantidad,
                )
            )
            await inventario_client.registrar_ingreso(
                producto_id=det.producto_id,
                almacen_id=payload.almacen_id,
                cantidad=float(det.cantidad),
                observaciones=f"Recepción {codigo} - OC {orden.codigo}",
            )

        orden.estado = EstadoDocumento.RECIBIDA.value
        await db.commit()

        await finanzas_client.crear_cuenta_por_pagar(
            referencia_tipo="ORDEN_COMPRA",
            referencia_id=orden.id,
            proveedor_id=orden.proveedor_id,
            monto=float(orden.total),
            descripcion=f"Cuenta por pagar OC {orden.codigo}",
        )

        return await crud_recepcion.get(db, recepcion.id)


compra_service = CompraService()
