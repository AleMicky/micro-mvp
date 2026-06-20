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
            proveedor = proveedores["PROV-001"]
            orden = OrdenCompra(
                codigo="OC-00001",
                proveedor_id=proveedor.id,
                estado=EstadoOrdenCompra.APROBADA.value,
                fecha="2026-06-01",
                total=Decimal("925.00"),
                observaciones="Orden demo leche PIL",
            )
            db.add(orden)
            await db.flush()
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden.id,
                    producto_id=1,
                    cantidad=Decimal("50"),
                    precio_unitario=Decimal("18.50"),
                    subtotal=Decimal("925.00"),
                )
            )
            await db.commit()
            logger.info("Orden de compra demo creada")

        stmt = select(RecepcionCompra).where(RecepcionCompra.codigo == "REC-00001")
        if not (await db.execute(stmt)).scalar_one_or_none():
            stmt_o = select(OrdenCompra).where(OrdenCompra.codigo == "OC-00001")
            orden = (await db.execute(stmt_o)).scalar_one()
            recepcion = RecepcionCompra(
                codigo="REC-00001",
                orden_id=orden.id,
                almacen_id=1,
                estado=EstadoRecepcionCompra.BORRADOR.value,
                fecha="2026-06-10",
                total=Decimal("925.00"),
                observaciones="Recepción demo orden 1",
            )
            db.add(recepcion)
            await db.flush()
            db.add(
                RecepcionCompraDetalle(
                    recepcion_id=recepcion.id,
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
