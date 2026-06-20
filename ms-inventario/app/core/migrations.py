import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

_ALMACENES_COLUMNAS = [
    "sucursal_id INTEGER",
    "sucursal_codigo VARCHAR(50)",
    "sucursal_nombre VARCHAR(200)",
    "compania_id INTEGER",
    "compania_nombre VARCHAR(200)",
]


async def run_migrations(engine: AsyncEngine) -> None:
    """Aplica cambios de esquema en volúmenes Postgres ya existentes."""
    async with engine.begin() as conn:
        for columna in _ALMACENES_COLUMNAS:
            await conn.execute(
                text(f"ALTER TABLE almacenes ADD COLUMN IF NOT EXISTS {columna}")
            )
    logger.info("Migraciones ms-inventario aplicadas")
