from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import chatbot, health, whatsapp_webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="MS Chatbot",
    description="Motor conversacional para atención al cliente y consulta de catálogo",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(health.router)
app.include_router(chatbot.router)
app.include_router(whatsapp_webhook.router)
