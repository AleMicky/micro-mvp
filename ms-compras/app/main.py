import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import cotizaciones, health, ordenes, ordenes_compra, proveedores, recepciones, recepciones_compra

logger = logging.getLogger(__name__)

_MIGRATIONS = [
    "ALTER TABLE orden_compra_detalles ADD COLUMN IF NOT EXISTS producto_codigo VARCHAR(50)",
    "ALTER TABLE orden_compra_detalles ADD COLUMN IF NOT EXISTS producto_nombre VARCHAR(200)",
    "ALTER TABLE recepciones_compra ADD COLUMN IF NOT EXISTS almacen_nombre VARCHAR(150)",
    "ALTER TABLE recepciones_compra ADD COLUMN IF NOT EXISTS sucursal_id INTEGER",
    "ALTER TABLE recepciones_compra ADD COLUMN IF NOT EXISTS sucursal_nombre VARCHAR(150)",
    "ALTER TABLE recepciones_compra ADD COLUMN IF NOT EXISTS compania_id INTEGER",
    "ALTER TABLE recepciones_compra ADD COLUMN IF NOT EXISTS compania_nombre VARCHAR(200)",
    "ALTER TABLE recepcion_compra_detalles ADD COLUMN IF NOT EXISTS producto_codigo VARCHAR(50)",
    "ALTER TABLE recepcion_compra_detalles ADD COLUMN IF NOT EXISTS producto_nombre VARCHAR(200)",
]


async def _run_migrations(conn) -> None:
    for stmt in _MIGRATIONS:
        await conn.execute(text(stmt))


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _run_migrations(conn)
    if settings.run_seed:
        from app.seed import run_seed

        logger.info("Ejecutando seed de ms-compras...")
        await run_seed()
    yield


app = FastAPI(
    title="MS Compras",
    description="Microservicio de gestión de compras",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(proveedores.router)
app.include_router(cotizaciones.router)
app.include_router(ordenes.router)
app.include_router(ordenes_compra.router)
app.include_router(recepciones.router)
app.include_router(recepciones_compra.router)
