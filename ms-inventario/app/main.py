import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.routers import almacenes, existencias, health, movimientos, stock

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
