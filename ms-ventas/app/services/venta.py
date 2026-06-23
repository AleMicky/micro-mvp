from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.ventas import _next_codigo, crud_cotizacion, crud_factura, crud_venta
from app.events.publisher import publish_event
from app.models import Factura, FacturaDetalle, Venta, VentaDetalle
from app.schemas.ventas import DetalleCreate, FacturaCreate, VentaCreate
from app.services.clients import catalogos_client, clientes_client, finanzas_client, inventario_client


class VentaService:
    async def procesar_venta_completa(self, db: AsyncSession, payload: VentaCreate):
        cliente = await clientes_client.validar_cliente(payload.cliente_id)

        for det in payload.detalles:
            await catalogos_client.obtener_producto(det.producto_id)
            await catalogos_client.verificar_stock(
                det.producto_id, payload.almacen_id, float(det.cantidad)
            )

        codigo = await _next_codigo(db, "VTA", Venta)
        total = sum(d.cantidad * d.precio_unitario for d in payload.detalles)
        venta = Venta(
            codigo=codigo,
            cliente_id=payload.cliente_id,
            cotizacion_id=payload.cotizacion_id,
            almacen_id=payload.almacen_id,
            estado="EN_PROCESO",
            fecha=payload.fecha or str(date.today()),
            observaciones=payload.observaciones,
            total=total,
        )
        db.add(venta)
        await db.flush()
        for d in payload.detalles:
            sub = d.cantidad * d.precio_unitario
            db.add(
                VentaDetalle(
                    venta_id=venta.id,
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio_unitario=d.precio_unitario,
                    subtotal=sub,
                )
            )
        await db.commit()

        await publish_event(
            "SaleCreated",
            {"venta_id": venta.id, "venta_codigo": codigo, "cliente_id": payload.cliente_id, "total": float(total)},
        )

        for det in payload.detalles:
            await inventario_client.registrar_salida(
                producto_id=det.producto_id,
                almacen_id=payload.almacen_id,
                cantidad=float(det.cantidad),
                observaciones=f"Venta {codigo}",
            )

        venta_obj = await crud_venta.get(db, venta.id)
        venta_obj.estado = "CONFIRMADA"
        await db.commit()

        factura = await self.crear_factura(
            db, FacturaCreate(venta_id=venta.id, impuesto=Decimal("0"))
        )

        puntos = int(sum(float(d.cantidad) * 5 for d in payload.detalles))
        await clientes_client.asignar_puntos(payload.cliente_id, puntos, referencia=codigo)

        await publish_event(
            "SaleCompleted",
            {
                "venta_id": venta.id,
                "venta_codigo": codigo,
                "cliente_id": payload.cliente_id,
                "cliente_nombre": cliente.get("nombre"),
                "total": float(total),
                "factura_id": factura.id,
                "factura_codigo": factura.codigo,
            },
        )

        venta_obj.estado = "COMPLETADA"
        await db.commit()
        return await crud_venta.get(db, venta.id)

    async def aprobar_cotizacion(self, db: AsyncSession, cotizacion_id: int) -> Venta:
        cotizacion = await crud_cotizacion.get(db, cotizacion_id)
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
        if cotizacion.estado not in ("BORRADOR", "PENDIENTE"):
            raise HTTPException(
                status_code=400, detail=f"No se puede aprobar una cotización en estado {cotizacion.estado}"
            )

        venta_payload = VentaCreate(
            cliente_id=cotizacion.cliente_id,
            cotizacion_id=cotizacion.id,
            almacen_id=cotizacion.almacen_id,
            observaciones=cotizacion.observaciones,
            detalles=[
                DetalleCreate(producto_id=d.producto_id, cantidad=d.cantidad, precio_unitario=d.precio_unitario)
                for d in cotizacion.detalles
            ],
        )
        venta = await self.procesar_venta_completa(db, venta_payload)

        cotizacion_obj = await crud_cotizacion.get(db, cotizacion_id)
        cotizacion_obj.estado = "CONFIRMADA"
        await db.commit()
        return venta

    async def confirmar_venta(self, db: AsyncSession, venta_id: int):
        venta = await crud_venta.get(db, venta_id)
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        if venta.estado not in ("BORRADOR", "PENDIENTE"):
            raise HTTPException(status_code=400, detail=f"No se puede confirmar venta en estado {venta.estado}")
        for det in venta.detalles:
            await inventario_client.registrar_salida(
                producto_id=det.producto_id,
                almacen_id=venta.almacen_id,
                cantidad=float(det.cantidad),
                observaciones=f"Venta {venta.codigo}",
            )
        venta.estado = "CONFIRMADA"
        await db.commit()
        return await crud_venta.get(db, venta_id)

    async def crear_factura(self, db: AsyncSession, payload: FacturaCreate):
        venta = await crud_venta.get(db, payload.venta_id)
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        if venta.estado not in ("CONFIRMADA", "EN_PROCESO", "COMPLETADA"):
            raise HTTPException(status_code=400, detail="La venta debe estar confirmada para facturar")
        codigo = await _next_codigo(db, "FAC", Factura)
        subtotal = venta.total
        impuesto = payload.impuesto
        total = subtotal + impuesto
        factura = Factura(
            codigo=codigo,
            venta_id=venta.id,
            estado="FACTURADA",
            fecha=payload.fecha or str(date.today()),
            subtotal=subtotal,
            impuesto=impuesto,
            total=total,
        )
        db.add(factura)
        await db.flush()
        for det in venta.detalles:
            db.add(
                FacturaDetalle(
                    factura_id=factura.id,
                    producto_id=det.producto_id,
                    cantidad=det.cantidad,
                    precio_unitario=det.precio_unitario,
                    subtotal=det.subtotal,
                )
            )
        venta.estado = "FACTURADA"
        await db.commit()
        await finanzas_client.crear_cuenta_por_cobrar(
            referencia_tipo="FACTURA",
            referencia_id=factura.id,
            cliente_id=venta.cliente_id,
            monto=float(total),
            descripcion=f"Cuenta por cobrar factura {codigo}",
        )
        return await crud_factura.get(db, factura.id)

    async def reporte_dia(self, db: AsyncSession, fecha: str | None = None) -> dict:
        dia = fecha or str(date.today())
        stmt = select(
            func.count(Venta.id),
            func.coalesce(func.sum(Venta.total), 0),
        ).where(Venta.fecha == dia, Venta.estado.in_(("CONFIRMADA", "FACTURADA", "COMPLETADA")))
        count, monto = (await db.execute(stmt)).one()
        ventas = await crud_venta.get_all(db, limit=500)
        del_dia = [v for v in ventas if v.fecha == dia]
        return {
            "fecha": dia,
            "total_ventas": int(count or 0),
            "monto_total": float(monto or 0),
            "ventas": del_dia,
        }


venta_service = VentaService()
