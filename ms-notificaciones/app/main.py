import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.events.consumer import start_consumer
from app.routers import health, notificaciones

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_consumer_connection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _consumer_connection
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.rabbitmq_url:
        for attempt in range(10):
            try:
                _consumer_connection = await start_consumer(settings.rabbitmq_url)
                break
            except Exception as exc:
                logger.warning("RabbitMQ no disponible (intento %s): %s", attempt + 1, exc)
                await asyncio.sleep(3)

    yield

    if _consumer_connection:
        await _consumer_connection.close()


app = FastAPI(
    title="MS Notificaciones",
    description="Microservicio de notificaciones simuladas vía eventos",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(health.router)
app.include_router(notificaciones.router)
