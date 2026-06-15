import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, health, permisos, roles, usuarios

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.run_seed:
        from app.seed import run_seed

        logger.info("Ejecutando seed de desarrollo...")
        await run_seed()
    yield


app = FastAPI(
    title="MS Auth",
    description="Microservicio de autenticación, usuarios, roles y permisos",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(roles.router)
app.include_router(permisos.router)
