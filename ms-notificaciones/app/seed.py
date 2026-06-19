"""
Seed idempotente para datos iniciales de ms-notificaciones.

Ejecución manual:
    python -m app.seed
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.database import async_session
from app.models.notificacion import Notificacion

logger = logging.getLogger(__name__)

# cliente_id=1 corresponde a Juanito Pérez en ms-clientes.
NOTIFICACIONES_SEED = [
    {
        "evento_origen": "SEED-SaleCompleted",
        "tipo": "VENTA",
        "contenido": "Venta completada para Juanito Pérez.",
        "cliente_id": 1,
    },
    {
        "evento_origen": "SEED-PointsAssigned",
        "tipo": "PUNTOS",
        "contenido": "Puntos asignados a Juanito Pérez.",
        "cliente_id": 1,
    },
    {
        "evento_origen": "SEED-TransferCompleted",
        "tipo": "TRANSFERENCIA",
        "contenido": "Transferencia completada entre Sucursal Prado y Sucursal El Alto.",
        "cliente_id": None,
    },
    {
        "evento_origen": "SEED-StockLow",
        "tipo": "STOCK",
        "contenido": "Stock bajo de producto Leche PIL 980cc en Sucursal Prado.",
        "cliente_id": None,
    },
]


async def _ensure_notificacion(db, data: dict) -> None:
    stmt = select(Notificacion).where(Notificacion.evento_origen == data["evento_origen"])
    if (await db.execute(stmt)).scalar_one_or_none():
        logger.info("Notificación ya existe: %s", data["evento_origen"])
        return

    db.add(Notificacion(**data))
    logger.info("Notificación creada: %s", data["tipo"])


async def run_seed() -> None:
    async with async_session() as db:
        for data in NOTIFICACIONES_SEED:
            await _ensure_notificacion(db, data)
        await db.commit()

    logger.info("Seed de ms-notificaciones completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
