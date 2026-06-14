from fastapi import FastAPI

from app.core.cors import setup_cors
from app.middleware.jwt import JWTPlaceholderMiddleware
from app.routers import health, proxy

app = FastAPI(
    title="API Gateway",
    description="Punto de entrada único para el frontend",
    version="0.1.0",
)

setup_cors(app)
app.add_middleware(JWTPlaceholderMiddleware)

app.include_router(health.router)
app.include_router(proxy.router)
