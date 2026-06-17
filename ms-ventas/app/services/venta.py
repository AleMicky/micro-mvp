from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.ventas import _next_codigo, crud_factura, crud_venta
from app.models import Factura, FacturaDetalle
from app.schemas.ventas import FacturaCreate
from app.services.clients import finanzas_client, inventario_client


class VentaService:
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
        if venta.estado != "CONFIRMADA":
            raise HTTPException(status_code=400, detail="La venta debe estar CONFIRMADA para facturar")
        codigo = await _next_codigo(db, "FAC", Factura)
        subtotal = venta.total
        impuesto = payload.impuesto
        total = subtotal + impuesto
        factura = Factura(codigo=codigo, venta_id=venta.id, estado="FACTURADA", fecha=payload.fecha, subtotal=subtotal, impuesto=impuesto, total=total)
        db.add(factura)
        await db.flush()
        for det in venta.detalles:
            db.add(FacturaDetalle(factura_id=factura.id, producto_id=det.producto_id, cantidad=det.cantidad, precio_unitario=det.precio_unitario, subtotal=det.subtotal))
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


venta_service = VentaService()
