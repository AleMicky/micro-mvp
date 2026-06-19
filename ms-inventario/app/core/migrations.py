import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def run_migrations(engine: AsyncEngine) -> None:
    """Aplica cambios de esquema en volúmenes Postgres ya existentes."""
    async with engine.begin() as conn:
        await conn.execute(
            text("ALTER TABLE almacenes ADD COLUMN IF NOT EXISTS sucursal_id INTEGER")
        )
    logger.info("Migraciones ms-inventario aplicadas")
