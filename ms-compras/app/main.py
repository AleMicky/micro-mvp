import logging
from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import cotizaciones, health, ordenes, proveedores, recepciones

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
app.include_router(recepciones.router)
