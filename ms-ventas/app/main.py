import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import clientes, cotizaciones, facturas, health, ventas

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if settings.run_seed:
        from app.seed import run_seed
        logger.info("Ejecutando seed ms-ventas...")
        await run_seed()
    yield


app = FastAPI(title="MS Ventas", version="0.1.0", lifespan=lifespan)
app.include_router(health.router)
app.include_router(clientes.router)
app.include_router(cotizaciones.router)
app.include_router(facturas.router)
app.include_router(ventas.router)
