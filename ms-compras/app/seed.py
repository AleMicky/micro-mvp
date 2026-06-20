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
    {
        "codigo": "PROV-001",
        "nombre": "PIL Bolivia S.A.",
        "rfc": "1001001001",
        "telefono": "70000001",
        "email": "ventas@pil.bo",
    },
    {
        "codigo": "PROV-002",
        "nombre": "Distribuidora Andina S.R.L.",
        "rfc": "1001001002",
        "telefono": "70000002",
        "email": "contacto@andina.bo",
    },
    {
        "codigo": "PROV-003",
        "nombre": "Importadora Santa Cruz Ltda.",
        "rfc": "1001001003",
        "telefono": "70000003",
        "email": "ventas@importsantacruz.bo",
    },
]


async def run_seed() -> None:
    async with async_session() as db:
        proveedores: dict[str, Proveedor] = {}
        for data in PROVEEDORES:
            stmt = select(Proveedor).where(
                (Proveedor.codigo == data["codigo"]) | (Proveedor.rfc == data["rfc"])
            )
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
                total=Decimal("1500.00"),
                observaciones="Orden demo leche PIL",
            )
            db.add(orden)
            await db.flush()
            db.add(
                OrdenCompraDetalle(
                    orden_id=orden.id,
                    producto_id=1,
                    producto_codigo="PROD-001",
                    producto_nombre="Leche PIL 980cc",
                    cantidad=Decimal("100"),
                    precio_unitario=Decimal("15.00"),
                    subtotal=Decimal("1500.00"),
                )
            )
            await db.commit()
            logger.info("Orden de compra demo creada: OC-00001")

        stmt = select(RecepcionCompra).where(RecepcionCompra.codigo == "REC-00001")
        if not (await db.execute(stmt)).scalar_one_or_none():
            stmt_o = select(OrdenCompra).where(OrdenCompra.codigo == "OC-00001")
            orden = (await db.execute(stmt_o)).scalar_one()
            recepcion = RecepcionCompra(
                codigo="REC-00001",
                orden_id=orden.id,
                almacen_id=1,
                almacen_nombre="Almacén General Central",
                sucursal_id=1,
                sucursal_nombre="Sucursal Central",
                compania_id=1,
                compania_nombre="Empresa Demo",
                estado=EstadoRecepcionCompra.BORRADOR.value,
                fecha="2026-06-10",
                total=Decimal("1500.00"),
                observaciones="Recepción demo OC-00001",
            )
            db.add(recepcion)
            await db.flush()
            db.add(
                RecepcionCompraDetalle(
                    recepcion_id=recepcion.id,
                    producto_id=1,
                    producto_codigo="PROD-001",
                    producto_nombre="Leche PIL 980cc",
                    cantidad_recibida=Decimal("100"),
                    costo_unitario=Decimal("15.00"),
                    subtotal=Decimal("1500.00"),
                )
            )
            await db.commit()
            logger.info("Recepción demo creada: REC-00001")

    logger.info("Seed ms-compras completado")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())
