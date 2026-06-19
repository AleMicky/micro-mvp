"""
Seed idempotente para datos iniciales de ms-ventas.

Ejecución manual:
    python -m app.seed
"""

import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.models import Cliente, Factura, FacturaDetalle, Venta, VentaDetalle

logger = logging.getLogger(__name__)

# IDs de productos según ms-catalogos (PROD-001=1, PROD-005=5).
PRODUCTO_LECHE_ID = 1
PRODUCTO_MAYONESA_ID = 5

# IDs de almacenes según ms-inventario (orden de creación).
ALMACEN_PRADO_ID = 3
ALMACEN_CENTRAL_ID = 1

CLIENTES_SEED = [
    {
        "codigo": "CLI-001",
        "nombre": "Juanito Pérez",
        "email": "juanito.perez@test.com",
        "telefono": "70000001",
    },
    {
        "codigo": "CLI-002",
        "nombre": "María López",
        "email": "maria.lopez@test.com",
        "telefono": "70000002",
    },
    {
        "codigo": "CLI-003",
        "nombre": "Carlos Rojas",
        "email": "carlos.rojas@test.com",
        "telefono": "70000003",
    },
]

VENTAS_SEED = [
    {
        "codigo": "VTA-00001",
        "cliente_codigo": "CLI-001",
        "almacen_id": ALMACEN_PRADO_ID,
        "estado": "COMPLETADA",
        "fecha": "2026-06-10",
        "observaciones": "Método de pago: EFECTIVO",
        "producto_id": PRODUCTO_LECHE_ID,
        "cantidad": Decimal("2"),
        "precio_unitario": Decimal("18.50"),
    },
    {
        "codigo": "VTA-00002",
        "cliente_codigo": "CLI-001",
        "almacen_id": ALMACEN_CENTRAL_ID,
        "estado": "COMPLETADA",
        "fecha": "2026-06-11",
        "observaciones": "Método de pago: TARJETA",
        "producto_id": PRODUCTO_MAYONESA_ID,
        "cantidad": Decimal("120"),
        "precio_unitario": Decimal("2.00"),
    },
]

FACTURAS_SEED = [
    {"codigo": "FAC-00001", "venta_codigo": "VTA-00001", "fecha": "2026-06-10"},
    {"codigo": "FAC-00002", "venta_codigo": "VTA-00002", "fecha": "2026-06-11"},
]


async def _ensure_cliente(db, data: dict) -> Cliente:
    stmt = select(Cliente).where(Cliente.codigo == data["codigo"])
    cliente = (await db.execute(stmt)).scalar_one_or_none()
    if cliente:
        logger.info("Cliente ya existe: %s", data["codigo"])
        return cliente
    cliente = Cliente(**data)
    db.add(cliente)
    await db.flush()
    logger.info("Cliente creado: %s", data["nombre"])
    return cliente


async def _ensure_venta(db, data: dict, clientes: dict[str, Cliente]) -> Venta | None:
    stmt = select(Venta).where(Venta.codigo == data["codigo"])
    venta = (await db.execute(stmt)).scalar_one_or_none()
    if venta:
        logger.info("Venta ya existe: %s", data["codigo"])
        return venta

    subtotal = data["cantidad"] * data["precio_unitario"]
    venta = Venta(
        codigo=data["codigo"],
        cliente_id=clientes[data["cliente_codigo"]].id,
        almacen_id=data["almacen_id"],
        estado=data["estado"],
        fecha=data["fecha"],
        observaciones=data["observaciones"],
        total=subtotal,
    )
    db.add(venta)
    await db.flush()
    db.add(
        VentaDetalle(
            venta_id=venta.id,
            producto_id=data["producto_id"],
            cantidad=data["cantidad"],
            precio_unitario=data["precio_unitario"],
            subtotal=subtotal,
        )
    )
    logger.info("Venta creada: %s", data["codigo"])
    return venta


async def _ensure_factura(db, data: dict) -> None:
    stmt = select(Factura).where(Factura.codigo == data["codigo"])
    if (await db.execute(stmt)).scalar_one_or_none():
        logger.info("Factura ya existe: %s", data["codigo"])
        return

    venta = (
        await db.execute(select(Venta).where(Venta.codigo == data["venta_codigo"]))
    ).scalar_one()

    detalle = (
        await db.execute(select(VentaDetalle).where(VentaDetalle.venta_id == venta.id))
    ).scalars().first()

    subtotal = detalle.subtotal if detalle else venta.total

    factura = Factura(
        codigo=data["codigo"],
        venta_id=venta.id,
        estado="FACTURADA",
        fecha=data["fecha"],
        subtotal=subtotal,
        impuesto=Decimal("0"),
        total=subtotal,
    )
    db.add(factura)
    await db.flush()

    if detalle:
        db.add(
            FacturaDetalle(
                factura_id=factura.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal,
            )
        )

    logger.info("Factura creada: %s", data["codigo"])


async def run_seed() -> None:
    async with async_session() as db:
        clientes: dict[str, Cliente] = {}
        for data in CLIENTES_SEED:
            clientes[data["codigo"]] = await _ensure_cliente(db, data)
        await db.commit()

        for data in VENTAS_SEED:
            await _ensure_venta(db, data, clientes)
        await db.commit()

        for data in FACTURAS_SEED:
            await _ensure_factura(db, data)
        await db.commit()

    logger.info("Seed de ms-ventas completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
