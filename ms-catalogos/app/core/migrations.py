import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def run_migrations(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE productos ADD COLUMN IF NOT EXISTS codigo_barras VARCHAR(50)"))
        await conn.execute(
            text("ALTER TABLE productos ADD COLUMN IF NOT EXISTS precio_base NUMERIC(15, 2) NOT NULL DEFAULT 0")
        )
        await conn.execute(
            text("ALTER TABLE productos ADD COLUMN IF NOT EXISTS estado VARCHAR(30) NOT NULL DEFAULT 'ACTIVO'")
        )
    logger.info("Migraciones ms-catalogos aplicadas")
