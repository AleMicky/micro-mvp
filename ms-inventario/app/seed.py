"""
Seed idempotente para datos de desarrollo de ms-inventario.

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

ALMACENES_SEED = [
    {"codigo": "ALM-CENTRAL", "nombre": "Almacén Central", "direccion": "Oficina principal"},
    {"codigo": "ALM-SUCURSAL", "nombre": "Almacén Sucursal", "direccion": "Sucursal secundaria"},
    {"codigo": "ALM-TALLER", "nombre": "Almacén Taller", "direccion": "Área de mantenimiento"},
]

EXISTENCIAS_SEED = [
    {
        "producto_id": 1,
        "almacen_codigo": "ALM-CENTRAL",
        "cantidad_actual": Decimal("50"),
        "stock_minimo": Decimal("10"),
        "stock_maximo": Decimal("200"),
    },
    {
        "producto_id": 2,
        "almacen_codigo": "ALM-CENTRAL",
        "cantidad_actual": Decimal("30"),
        "stock_minimo": Decimal("5"),
        "stock_maximo": Decimal("100"),
    },
    {
        "producto_id": 3,
        "almacen_codigo": "ALM-SUCURSAL",
        "cantidad_actual": Decimal("15"),
        "stock_minimo": Decimal("5"),
        "stock_maximo": Decimal("80"),
    },
    {
        "producto_id": 4,
        "almacen_codigo": "ALM-TALLER",
        "cantidad_actual": Decimal("8"),
        "stock_minimo": Decimal("2"),
        "stock_maximo": Decimal("50"),
    },
]

SEED_OBSERVACION = "Carga inicial de inventario (seed)"


async def _get_almacen_por_codigo(db, codigo: str) -> Almacen | None:
    stmt = select(Almacen).where(Almacen.codigo == codigo)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


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
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def run_seed() -> None:
    async with async_session() as db:
        almacenes_por_codigo: dict[str, Almacen] = {}

        for data in ALMACENES_SEED:
            almacen = await _get_almacen_por_codigo(db, data["codigo"])
            if not almacen:
                almacen = Almacen(**data)
                db.add(almacen)
                await db.flush()
                logger.info("Almacén creado: %s", data["codigo"])
            else:
                logger.info("Almacén ya existe: %s", data["codigo"])
            almacenes_por_codigo[data["codigo"]] = almacen

        await db.commit()

        for item in EXISTENCIAS_SEED:
            almacen = almacenes_por_codigo[item["almacen_codigo"]]

            existencia = await crud_existencia.get_by_producto_almacen(
                db,
                producto_id=item["producto_id"],
                almacen_id=almacen.id,
            )

            if existencia:
                logger.info(
                    "Existencia ya existe: producto %s en %s",
                    item["producto_id"],
                    item["almacen_codigo"],
                )
            else:
                existencia = await crud_existencia.create(
                    db,
                    producto_id=item["producto_id"],
                    almacen_id=almacen.id,
                    cantidad_actual=item["cantidad_actual"],
                    stock_minimo=item["stock_minimo"],
                    stock_maximo=item["stock_maximo"],
                )
                logger.info(
                    "Existencia creada: producto %s en %s",
                    item["producto_id"],
                    item["almacen_codigo"],
                )

            if await _existe_movimiento_inicial(
                db,
                producto_id=item["producto_id"],
                almacen_id=almacen.id,
                cantidad=item["cantidad_actual"],
            ):
                logger.info(
                    "Movimiento inicial ya existe: producto %s en %s",
                    item["producto_id"],
                    item["almacen_codigo"],
                )
                continue

            movimiento = MovimientoInventario(
                tipo=TipoMovimiento.INGRESO.value,
                producto_id=item["producto_id"],
                almacen_id=almacen.id,
                cantidad=item["cantidad_actual"],
                cantidad_anterior=Decimal("0"),
                cantidad_nueva=item["cantidad_actual"],
                referencia_tipo=ReferenciaTipo.INGRESO.value,
                observaciones=SEED_OBSERVACION,
            )
            db.add(movimiento)
            logger.info(
                "Movimiento INGRESO creado: producto %s en %s",
                item["producto_id"],
                item["almacen_codigo"],
            )

        await db.commit()

    logger.info("Seed de ms-inventario completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
