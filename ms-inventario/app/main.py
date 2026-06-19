import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine
from app.core.migrations import run_migrations
from app.routers import almacenes, existencias, health, inventario, movimientos, stock

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_migrations(engine)
    if settings.run_seed:
        from app.seed import run_seed

        logger.info("Ejecutando seed de desarrollo...")
        await run_seed()
    yield


app = FastAPI(
    title="MS Inventario",
    description="Microservicio de gestión de inventario (almacenes, existencias, movimientos)",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(almacenes.router)
app.include_router(existencias.router)
app.include_router(movimientos.router)
app.include_router(stock.router)
app.include_router(inventario.router)
