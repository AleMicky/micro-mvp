import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import companias, health, sucursales

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if settings.run_seed:
        from app.seed import run_seed

        logger.info("Ejecutando seed ms-company...")
        await run_seed()
    yield


app = FastAPI(
    title="MS Company",
    description="Microservicio de compañías, sucursales y ciudades",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(health.router)
app.include_router(companias.router)
app.include_router(sucursales.router)
