from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine
from app.core.migrations import run_migrations
from app.routers import categorias, health, marcas, productos, unidades_medida


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_migrations(engine)
    yield


app = FastAPI(
    title="MS Catálogos",
    description="Microservicio de gestión de catálogos (productos, categorías, marcas, unidades)",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(categorias.router)
app.include_router(marcas.router)
app.include_router(unidades_medida.router)
app.include_router(productos.router)
