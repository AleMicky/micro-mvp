"""Seed idempotente para ms-compras."""

import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.models import (
    OrdenCompra,
    OrdenCompraDetalle,
    Proveedor,
    RecepcionCompra,
    RecepcionCompraDetalle,
)

logger = logging.getLogger(__name__)

PROVEEDORES = [
    {"codigo": "PROV-001", "nombre": "Distribuidora Norte SA", "rfc": "DNO900101ABC", "email": "ventas@norte.com"},
    {"codigo": "PROV-002", "nombre": "Suministros del Centro", "rfc": "SCO880202XYZ", "email": "contacto@centro.com"},
    {"codigo": "PROV-003", "nombre": "Importadora Global", "rfc": "IGL770303GHI", "email": "info@global.com"},
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
                logger.info("Proveedor creado: %s", data["codigo"])
            proveedores[data["codigo"]] = prov

        await db.commit()

        stmt = select(OrdenCompra).where(OrdenCompra.codigo == "OC-00001")
        if not (await db.execute(stmt)).scalar_one_or_none():
            p1 = proveedores["PROV-001"]
            orden1 = OrdenCompra(
                codigo="OC-00001",
                proveedor_id=p1.id,
                estado="APROBADA",
                fecha="2026-06-01",
                total=Decimal("1500.00"),
                observaciones="Orden demo 1",
            )
            db.add(orden1)
            await db.flush()
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden1.id,
                    producto_id=1,
                    cantidad=Decimal("10"),
                    precio_unitario=Decimal("100.00"),
                    subtotal=Decimal("1000.00"),
                )
            )
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden1.id,
                    producto_id=2,
                    cantidad=Decimal("5"),
                    precio_unitario=Decimal("100.00"),
                    subtotal=Decimal("500.00"),
                )
            )

            p2 = proveedores["PROV-002"]
            orden2 = OrdenCompra(
                codigo="OC-00002",
                proveedor_id=p2.id,
                estado="PENDIENTE",
                fecha="2026-06-05",
                total=Decimal("800.00"),
                observaciones="Orden demo 2",
            )
            db.add(orden2)
            await db.flush()
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden2.id,
                    producto_id=3,
                    cantidad=Decimal("8"),
                    precio_unitario=Decimal("100.00"),
                    subtotal=Decimal("800.00"),
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
                estado="RECIBIDA",
                fecha="2026-06-10",
                observaciones="Recepción parcial demo",
            )
            db.add(rec1)
            await db.flush()
            db.add(RecepcionCompraDetalle(recepcion_id=rec1.id, producto_id=1, cantidad=Decimal("10")))

            rec2 = RecepcionCompra(
                codigo="REC-00002",
                orden_id=orden.id,
                almacen_id=1,
                estado="RECIBIDA",
                fecha="2026-06-11",
                observaciones="Recepción complemento demo",
            )
            db.add(rec2)
            await db.flush()
            db.add(RecepcionCompraDetalle(recepcion_id=rec2.id, producto_id=2, cantidad=Decimal("5")))
            await db.commit()
            logger.info("Recepciones demo creadas")

    logger.info("Seed ms-compras completado")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())
