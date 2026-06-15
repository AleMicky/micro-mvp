from fastapi import FastAPI

from app.core.cors import setup_cors
from app.middleware.jwt import JWTAuthMiddleware
from app.routers import health, proxy

app = FastAPI(
    title="API Gateway",
    description="Punto de entrada único para el frontend",
    version="0.1.0",
)

setup_cors(app)
app.add_middleware(JWTAuthMiddleware)

app.include_router(health.router)
app.include_router(proxy.router)
