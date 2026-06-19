import json
import logging

import aio_pika
from sqlalchemy import select

from app.core.database import async_session
from app.models.notificacion import Notificacion

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "micro_mvp_events"
QUEUE_NAME = "ms_notificaciones_queue"
EVENTOS_CONSUMIDOS = {
    "SaleCompleted",
    "TransferCompleted",
    "PointsAssigned",
    "PromotionCreated",
}


def _build_contenido(event_type: str, payload: dict) -> tuple[str, str, int | None]:
    cliente_id = payload.get("cliente_id")
    if event_type == "SaleCompleted":
        return (
            "VENTA",
            f"Venta completada por Bs {payload.get('total', 'N/A')}. Ref: {payload.get('venta_codigo', '')}",
            cliente_id,
        )
    if event_type == "TransferCompleted":
        return (
            "TRANSFERENCIA",
            f"Transferencia de {payload.get('cantidad', '')} unidades del producto {payload.get('producto_id', '')} "
            f"desde sucursal {payload.get('origen', '')} a {payload.get('destino', '')}",
            None,
        )
    if event_type == "PointsAssigned":
        return (
            "PUNTOS",
            f"Se asignaron {payload.get('puntos', 0)} puntos al cliente {cliente_id}",
            cliente_id,
        )
    if event_type == "PromotionCreated":
        return (
            "PROMOCION",
            f"Nueva promoción: {payload.get('nombre', 'Promoción')}",
            cliente_id,
        )
    return ("INFO", json.dumps(payload), cliente_id)


async def _guardar_notificacion(event_type: str, payload: dict) -> None:
    tipo, contenido, cliente_id = _build_contenido(event_type, payload)
    async with async_session() as db:
        db.add(
            Notificacion(
                cliente_id=cliente_id,
                tipo=tipo,
                contenido=contenido,
                evento_origen=event_type,
            )
        )
        await db.commit()
    logger.info("Notificación registrada: %s", event_type)


async def _on_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            event_type = data.get("event_type", message.routing_key)
            payload = data.get("payload", {})
            if event_type in EVENTOS_CONSUMIDOS:
                await _guardar_notificacion(event_type, payload)
        except Exception as exc:
            logger.error("Error procesando mensaje: %s", exc)


async def start_consumer(rabbitmq_url: str) -> aio_pika.RobustConnection:
    connection = await aio_pika.connect_robust(rabbitmq_url)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True)
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    for event in EVENTOS_CONSUMIDOS:
        await queue.bind(exchange, routing_key=event)

    await queue.consume(_on_message)
    logger.info("Consumer RabbitMQ iniciado, escuchando: %s", EVENTOS_CONSUMIDOS)
    return connection
