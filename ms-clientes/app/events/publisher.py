import json
import logging
from typing import Any

import aio_pika

from app.core.config import settings

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "micro_mvp_events"


async def publish_event(event_type: str, payload: dict[str, Any]) -> None:
    if not settings.rabbitmq_url:
        logger.warning("RabbitMQ no configurado, evento %s omitido", event_type)
        return
    try:
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
            )
            message = aio_pika.Message(
                body=json.dumps({"event_type": event_type, "payload": payload}).encode(),
                content_type="application/json",
            )
            await exchange.publish(message, routing_key=event_type)
            logger.info("Evento publicado: %s", event_type)
    except Exception as exc:
        logger.error("Error publicando evento %s: %s", event_type, exc)
