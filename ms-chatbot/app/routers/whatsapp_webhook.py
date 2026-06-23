import asyncio
import hashlib
import hmac
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services import bot
from app.services.bot_config import MENSAJE_ERROR_SERVICIO
from app.services.conversacion import conversacion_service
from app.services.mensaje import mensaje_service
from app.services.static_media import obtener_logo
from app.services.whatsapp import whatsapp_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot/webhook", tags=["whatsapp-webhook"])


@router.get("/whatsapp")
async def verificar_webhook(request: Request):
    modo = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if modo == "subscribe" and token == settings.whatsapp_verify_token:
        return PlainTextResponse(content=challenge or "", status_code=200)

    raise HTTPException(status_code=403, detail="Verificación fallida")


def _extraer_texto(message: dict) -> str | None:
    tipo = message.get("type")
    if tipo == "text":
        return message.get("text", {}).get("body", "")
    if tipo == "interactive":
        interactive = message.get("interactive", {})
        if interactive.get("type") == "list_reply":
            return interactive.get("list_reply", {}).get("title", "")
        if interactive.get("type") == "button_reply":
            return interactive.get("button_reply", {}).get("title", "")
    return None


async def _procesar_mensaje_entrante(db: AsyncSession, message: dict) -> None:
    message_id = message.get("id")
    from_numero = message.get("from")

    if not from_numero:
        return

    if message_id and await mensaje_service.existe_por_wa_id(db, message_id):
        return

    texto = _extraer_texto(message)
    if texto is None:
        logger.info("Tipo de mensaje no soportado: %s de %s", message.get("type"), from_numero)
        return

    if message_id:
        await whatsapp_client.marcar_como_leido_con_typing(message_id)

    conversacion = await conversacion_service.get_or_create_whatsapp(db, from_numero)
    await mensaje_service.crear(db, conversacion.id, "entrante", texto, wa_message_id=message_id, origen="cliente")

    try:
        resultado = await bot.procesar_mensaje(db, from_numero, texto)
    except HTTPException:
        await mensaje_service.crear(db, conversacion.id, "saliente", MENSAJE_ERROR_SERVICIO)
        await whatsapp_client.enviar_texto(from_numero, MENSAJE_ERROR_SERVICIO)
        return

    await mensaje_service.crear(db, conversacion.id, "saliente", resultado.respuesta)
    if resultado.opciones:
        await whatsapp_client.enviar_lista(from_numero, resultado.respuesta, resultado.opciones)
    else:
        await whatsapp_client.enviar_texto(from_numero, resultado.respuesta)

    if resultado.ubicaciones_pendientes:
        await asyncio.gather(
            *(
                whatsapp_client.enviar_ubicacion(
                    from_numero,
                    ubicacion["latitud"],
                    ubicacion["longitud"],
                    ubicacion["nombre"],
                    ubicacion["direccion"],
                )
                for ubicacion in resultado.ubicaciones_pendientes
            )
        )
        for ubicacion in resultado.ubicaciones_pendientes:
            await mensaje_service.crear(
                db, conversacion.id, "saliente", f"📍 {ubicacion['nombre']}", tipo_mensaje="ubicacion"
            )

    if resultado.enviar_logo:
        logo = obtener_logo()
        if not logo:
            logger.warning("Logo no encontrado en static/logo.png")
        else:
            media_id = await whatsapp_client.subir_media(logo, "image/png", "logo.png")
            if not media_id:
                logger.warning("No se pudo subir el logo a WhatsApp (conversacion_id=%s)", conversacion.id)
            else:
                envio = await whatsapp_client.enviar_imagen(from_numero, media_id)
                if not envio.get("error"):
                    await mensaje_service.crear(db, conversacion.id, "saliente", "🖼️ logo.png", tipo_mensaje="imagen")
                else:
                    logger.warning(
                        "Reintentando envío de logo tras fallo (conversacion_id=%s): %s",
                        conversacion.id,
                        envio.get("error"),
                    )
                    envio_retry = await whatsapp_client.enviar_imagen(from_numero, media_id)
                    if not envio_retry.get("error"):
                        await mensaje_service.crear(
                            db, conversacion.id, "saliente", "🖼️ logo.png", tipo_mensaje="imagen"
                        )
                    else:
                        logger.warning(
                            "No se pudo enviar el logo tras reintento (conversacion_id=%s): %s",
                            conversacion.id,
                            envio_retry.get("error"),
                        )

    if resultado.pdf_pendiente:
        media_id = await whatsapp_client.subir_media(
            resultado.pdf_pendiente, "application/pdf", resultado.pdf_nombre
        )
        if media_id:
            await whatsapp_client.enviar_documento(from_numero, media_id, resultado.pdf_nombre)
            await mensaje_service.crear(
                db,
                conversacion.id,
                "saliente",
                resultado.pdf_nombre,
                tipo_mensaje="documento",
                nombre_archivo=resultado.pdf_nombre,
            )
        else:
            logger.warning("Pedido confirmado pero no se pudo enviar el PDF (conversacion_id=%s)", conversacion.id)


@router.post("/whatsapp")
async def recibir_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    raw_body = await request.body()

    if settings.whatsapp_app_secret:
        firma = request.headers.get("x-hub-signature-256", "")
        esperada = "sha256=" + hmac.new(
            settings.whatsapp_app_secret.encode(), raw_body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(esperada, firma):
            raise HTTPException(status_code=403, detail="Firma inválida")

    payload = json.loads(raw_body or b"{}")

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "statuses" in value:
                continue
            for message in value.get("messages", []):
                await _procesar_mensaje_entrante(db, message)

    return {"status": "ok"}
