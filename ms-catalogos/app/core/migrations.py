import logging
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

STATIC_PRODUCTOS_DIR = Path(__file__).resolve().parent.parent / "static" / "productos"


async def run_migrations(engine: AsyncEngine) -> None:
    STATIC_PRODUCTOS_DIR.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE productos ADD COLUMN IF NOT EXISTS codigo_barras VARCHAR(50)"))
        await conn.execute(
            text("ALTER TABLE productos ADD COLUMN IF NOT EXISTS precio_base NUMERIC(15, 2) NOT NULL DEFAULT 0")
        )
        await conn.execute(
            text("ALTER TABLE productos ADD COLUMN IF NOT EXISTS estado VARCHAR(30) NOT NULL DEFAULT 'ACTIVO'")
        )
        await conn.execute(text("ALTER TABLE productos ADD COLUMN IF NOT EXISTS imagen_url VARCHAR(500)"))
        await conn.execute(
            text("""
                CREATE TABLE IF NOT EXISTS precios_producto (
                    id              SERIAL          PRIMARY KEY,
                    producto_id     INTEGER         NOT NULL,
                    precio_venta    NUMERIC(15, 2)  NOT NULL,
                    fecha_inicio    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
                    fecha_fin       TIMESTAMPTZ,
                    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
                    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
                    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
                    CONSTRAINT fk_precios_producto_producto
                        FOREIGN KEY (producto_id) REFERENCES productos (id)
                )
            """)
        )
        await conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_precios_producto_producto_id ON precios_producto (producto_id)")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_precios_producto_activo "
                "ON precios_producto (producto_id, activo) WHERE activo = TRUE"
            )
        )
    logger.info("Migraciones ms-catalogos aplicadas")
