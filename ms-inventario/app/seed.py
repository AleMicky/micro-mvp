"""
Seed idempotente para datos de desarrollo de ms-inventario.

Requiere que ms-company y ms-catalogos hayan ejecutado su seed primero
para mantener la correspondencia de sucursal_id y producto_id.

Ejecución manual:
    python -m app.seed
"""

import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.crud.existencia import crud_existencia
from app.enums.tipo_movimiento import ReferenciaTipo, TipoMovimiento
from app.models.almacen import Almacen
from app.models.movimiento_inventario import MovimientoInventario

logger = logging.getLogger(__name__)

# IDs esperados según orden de inserción en ms-company (seed idempotente).
SUCURSAL_ID_BY_CODIGO = {
    "SUC-CENTRAL": 1,
    "SUC-NORTE": 2,
    "SUC-PRADO": 3,
    "SUC-ALTO": 4,
    "SUC-HIPER-1": 5,
    "SUC-MELCHOR": 6,
}

# IDs esperados según orden de inserción en ms-catalogos.
PRODUCTO_ID_BY_CODIGO = {
    "PROD-001": 1,
    "PROD-002": 2,
    "PROD-003": 3,
    "PROD-004": 4,
    "PROD-005": 5,
    "PROD-006": 6,
}

ALMACENES_SEED = [
    {
        "codigo": "ALM-CENTRAL",
        "nombre": "Almacén Central",
        "direccion": "SuperMarket Bolivia - Central",
        "sucursal_codigo": "SUC-CENTRAL",
    },
    {
        "codigo": "ALM-NORTE",
        "nombre": "Almacén Zona Norte",
        "direccion": "SuperMarket Bolivia - Zona Norte",
        "sucursal_codigo": "SUC-NORTE",
    },
    {
        "codigo": "ALM-PRADO",
        "nombre": "Almacén Sucursal Prado",
        "direccion": "OXXO Bolivia - Sucursal Prado",
        "sucursal_codigo": "SUC-PRADO",
    },
    {
        "codigo": "ALM-ALTO",
        "nombre": "Almacén Sucursal El Alto",
        "direccion": "OXXO Bolivia - Sucursal El Alto",
        "sucursal_codigo": "SUC-ALTO",
    },
    {
        "codigo": "ALM-HIPER-1",
        "nombre": "Almacén Hipermaxi Sucursal 1",
        "direccion": "Hipermaxi - Sucursal 1",
        "sucursal_codigo": "SUC-HIPER-1",
    },
    {
        "codigo": "ALM-MELCHOR",
        "nombre": "Almacén Melchor Pérez",
        "direccion": "IC Norte - Melchor Pérez",
        "sucursal_codigo": "SUC-MELCHOR",
    },
]

EXISTENCIAS_SEED = [
    {"producto_codigo": "PROD-001", "almacen_codigo": "ALM-HIPER-1", "cantidad_actual": Decimal("18")},
    {"producto_codigo": "PROD-001", "almacen_codigo": "ALM-MELCHOR", "cantidad_actual": Decimal("85")},
    {"producto_codigo": "PROD-001", "almacen_codigo": "ALM-PRADO", "cantidad_actual": Decimal("48")},
    {"producto_codigo": "PROD-001", "almacen_codigo": "ALM-ALTO", "cantidad_actual": Decimal("50")},
    {"producto_codigo": "PROD-002", "almacen_codigo": "ALM-CENTRAL", "cantidad_actual": Decimal("120")},
    {"producto_codigo": "PROD-002", "almacen_codigo": "ALM-NORTE", "cantidad_actual": Decimal("60")},
    {"producto_codigo": "PROD-003", "almacen_codigo": "ALM-CENTRAL", "cantidad_actual": Decimal("80")},
    {"producto_codigo": "PROD-003", "almacen_codigo": "ALM-PRADO", "cantidad_actual": Decimal("40")},
    {"producto_codigo": "PROD-004", "almacen_codigo": "ALM-CENTRAL", "cantidad_actual": Decimal("90")},
    {"producto_codigo": "PROD-004", "almacen_codigo": "ALM-ALTO", "cantidad_actual": Decimal("35")},
    {"producto_codigo": "PROD-005", "almacen_codigo": "ALM-CENTRAL", "cantidad_actual": Decimal("120")},
    {"producto_codigo": "PROD-005", "almacen_codigo": "ALM-MELCHOR", "cantidad_actual": Decimal("80")},
]

SEED_OBSERVACION = "Carga inicial de inventario (seed)"


async def _get_almacen_por_codigo(db, codigo: str) -> Almacen | None:
    stmt = select(Almacen).where(Almacen.codigo == codigo)
    return (await db.execute(stmt)).scalar_one_or_none()


async def _existe_movimiento_inicial(
    db,
    *,
    producto_id: int,
    almacen_id: int,
    cantidad: Decimal,
) -> bool:
    stmt = select(MovimientoInventario).where(
        MovimientoInventario.producto_id == producto_id,
        MovimientoInventario.almacen_id == almacen_id,
        MovimientoInventario.tipo == TipoMovimiento.INGRESO.value,
        MovimientoInventario.cantidad == cantidad,
        MovimientoInventario.observaciones == SEED_OBSERVACION,
    )
    return (await db.execute(stmt)).scalar_one_or_none() is not None


async def run_seed() -> None:
    async with async_session() as db:
        almacenes_por_codigo: dict[str, Almacen] = {}

        for data in ALMACENES_SEED:
            almacen = await _get_almacen_por_codigo(db, data["codigo"])
            sucursal_id = SUCURSAL_ID_BY_CODIGO[data["sucursal_codigo"]]

            if not almacen:
                almacen = Almacen(
                    codigo=data["codigo"],
                    nombre=data["nombre"],
                    direccion=data["direccion"],
                    sucursal_id=sucursal_id,
                )
                db.add(almacen)
                await db.flush()
                logger.info("Almacén creado: %s", data["codigo"])
            else:
                logger.info("Almacén ya existe: %s", data["codigo"])

            almacenes_por_codigo[data["codigo"]] = almacen

        await db.commit()

        for item in EXISTENCIAS_SEED:
            producto_id = PRODUCTO_ID_BY_CODIGO[item["producto_codigo"]]
            almacen = almacenes_por_codigo[item["almacen_codigo"]]

            existencia = await crud_existencia.get_by_producto_almacen(
                db,
                producto_id=producto_id,
                almacen_id=almacen.id,
            )

            if existencia:
                logger.info(
                    "Existencia ya existe: %s en %s",
                    item["producto_codigo"],
                    item["almacen_codigo"],
                )
            else:
                await crud_existencia.create(
                    db,
                    producto_id=producto_id,
                    almacen_id=almacen.id,
                    cantidad_actual=item["cantidad_actual"],
                    stock_minimo=Decimal("10"),
                    stock_maximo=Decimal("500"),
                )
                logger.info(
                    "Existencia creada: %s en %s",
                    item["producto_codigo"],
                    item["almacen_codigo"],
                )

            if await _existe_movimiento_inicial(
                db,
                producto_id=producto_id,
                almacen_id=almacen.id,
                cantidad=item["cantidad_actual"],
            ):
                logger.info(
                    "Movimiento inicial ya existe: %s en %s",
                    item["producto_codigo"],
                    item["almacen_codigo"],
                )
                continue

            movimiento = MovimientoInventario(
                tipo=TipoMovimiento.INGRESO.value,
                producto_id=producto_id,
                almacen_id=almacen.id,
                cantidad=item["cantidad_actual"],
                cantidad_anterior=Decimal("0"),
                cantidad_nueva=item["cantidad_actual"],
                referencia_tipo=ReferenciaTipo.INGRESO.value,
                observaciones=SEED_OBSERVACION,
            )
            db.add(movimiento)
            logger.info(
                "Movimiento INGRESO creado: %s en %s",
                item["producto_codigo"],
                item["almacen_codigo"],
            )

        await db.commit()

    logger.info("Seed de ms-inventario completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
