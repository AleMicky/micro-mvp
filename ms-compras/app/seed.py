"""Seed idempotente para ms-compras."""

import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.enums.estado import EstadoOrdenCompra, EstadoRecepcionCompra
from app.models import (
    OrdenCompra,
    OrdenCompraDetalle,
    Proveedor,
    RecepcionCompra,
    RecepcionCompraDetalle,
)

logger = logging.getLogger(__name__)

PROVEEDORES = [
    {"codigo": "PROV-001", "nombre": "Distribuidora Bolivia S.R.L.", "email": "ventas@bolivia.com"},
    {"codigo": "PROV-002", "nombre": "Importadora Andina S.A.", "email": "contacto@andina.com"},
    {"codigo": "PROV-003", "nombre": "Proveedor Local Cochabamba", "email": "info@cochabamba.com"},
]


async def run_seed() -> None:
    async with async_session() as db:
        proveedores: dict[str, Proveedor] = {}
        for data in PROVEEDORES:
            stmt = select(Proveedor).where(Proveedor.codigo == data["codigo"])
            prov = (await db.execute(stmt)).scalar_one_or_none()
            if not prov:
                prov = Proveedor(**data)
                db.add(prov)
                await db.flush()
                logger.info("Proveedor creado: %s", data["nombre"])
            proveedores[data["codigo"]] = prov

        await db.commit()

        stmt = select(OrdenCompra).where(OrdenCompra.codigo == "OC-00001")
        if not (await db.execute(stmt)).scalar_one_or_none():
            p1 = proveedores["PROV-001"]
            orden1 = OrdenCompra(
                codigo="OC-00001",
                proveedor_id=p1.id,
                estado=EstadoOrdenCompra.APROBADA.value,
                fecha="2026-06-01",
                total=Decimal("925.00"),
                observaciones="Orden demo producto 1",
            )
            db.add(orden1)
            await db.flush()
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden1.id,
                    producto_id=1,
                    cantidad=Decimal("50"),
                    precio_unitario=Decimal("18.50"),
                    subtotal=Decimal("925.00"),
                )
            )

            p2 = proveedores["PROV-002"]
            orden2 = OrdenCompra(
                codigo="OC-00002",
                proveedor_id=p2.id,
                estado=EstadoOrdenCompra.BORRADOR.value,
                fecha="2026-06-05",
                total=Decimal("360.00"),
                observaciones="Orden demo producto 2",
            )
            db.add(orden2)
            await db.flush()
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden2.id,
                    producto_id=2,
                    cantidad=Decimal("30"),
                    precio_unitario=Decimal("12.00"),
                    subtotal=Decimal("360.00"),
                )
            )
            await db.commit()
            logger.info("Órdenes de compra demo creadas")

        stmt = select(RecepcionCompra).where(RecepcionCompra.codigo == "REC-00001")
        if not (await db.execute(stmt)).scalar_one_or_none():
            stmt_o = select(OrdenCompra).where(OrdenCompra.codigo == "OC-00001")
            orden = (await db.execute(stmt_o)).scalar_one()
            rec1 = RecepcionCompra(
                codigo="REC-00001",
                orden_id=orden.id,
                almacen_id=1,
                estado=EstadoRecepcionCompra.BORRADOR.value,
                fecha="2026-06-10",
                total=Decimal("925.00"),
                observaciones="Recepción demo orden 1",
            )
            db.add(rec1)
            await db.flush()
            db.add(
                RecepcionCompraDetalle(
                    recepcion_id=rec1.id,
                    producto_id=1,
                    cantidad_recibida=Decimal("50"),
                    costo_unitario=Decimal("18.50"),
                    subtotal=Decimal("925.00"),
                )
            )
            await db.commit()
            logger.info("Recepción demo creada")

    logger.info("Seed ms-compras completado")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())
