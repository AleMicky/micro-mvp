import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine
from app.core.migrations import run_migrations
from app.routers import categorias, health, marcas, productos, unidades_medida

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    (STATIC_DIR / "productos").mkdir(parents=True, exist_ok=True)
    await run_migrations(engine)
    if settings.run_seed:
        from app.seed import run_seed

        logger.info("Ejecutando seed ms-catalogos...")
        await run_seed()
    yield


app = FastAPI(
    title="MS Catálogos",
    description="Microservicio de gestión de catálogos (productos, categorías, marcas, unidades)",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(health.router)
app.include_router(categorias.router)
app.include_router(marcas.router)
app.include_router(unidades_medida.router)
app.include_router(productos.router)
