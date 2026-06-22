import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mensaje import ChatbotMensaje
from app.services.adjuntos import clasificar_adjunto, limite_para
from app.services.conversacion import conversacion_service
from app.services.mensaje import mensaje_service
from app.services.whatsapp import whatsapp_client

logger = logging.getLogger(__name__)


class RespuestaAgenteService:
    async def responder(self, db: AsyncSession, conversacion_id: int, texto: str) -> ChatbotMensaje:
        conversacion = await conversacion_service.get_by_id(db, conversacion_id)
        if not conversacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
        if conversacion.canal != "whatsapp":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede responder manualmente a conversaciones de WhatsApp",
            )

        mensaje = await mensaje_service.crear(db, conversacion.id, "saliente", texto, origen="agente")

        resultado_envio = await whatsapp_client.enviar_texto(conversacion.sesion_id, texto)
        if "error" in resultado_envio:
            logger.warning(
                "Mensaje de agente guardado pero no se pudo enviar por WhatsApp (conversacion_id=%s): %s",
                conversacion_id,
                resultado_envio["error"],
            )

        return mensaje

    async def responder_con_adjunto(
        self,
        db: AsyncSession,
        conversacion_id: int,
        contenido: bytes,
        content_type: str,
        filename: str,
        caption: str | None,
    ) -> ChatbotMensaje:
        conversacion = await conversacion_service.get_by_id(db, conversacion_id)
        if not conversacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
        if conversacion.canal != "whatsapp":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede responder manualmente a conversaciones de WhatsApp",
            )

        try:
            tipo_mensaje = clasificar_adjunto(content_type, filename)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de archivo no permitido. Use JPG, PNG, WEBP, PDF, DOC, DOCX, XLS o XLSX",
            )

        if len(contenido) > limite_para(tipo_mensaje):
            limite_mb = limite_para(tipo_mensaje) // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo supera el límite de {limite_mb}MB",
            )

        media_id = await whatsapp_client.subir_media(contenido, content_type, filename)
        if media_id is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo subir el archivo a WhatsApp. Intenta nuevamente",
            )

        texto_persistido = caption.strip() if caption and caption.strip() else filename
        mensaje = await mensaje_service.crear(
            db,
            conversacion.id,
            "saliente",
            texto_persistido,
            origen="agente",
            tipo_mensaje=tipo_mensaje,
            nombre_archivo=filename,
        )

        if tipo_mensaje == "imagen":
            resultado_envio = await whatsapp_client.enviar_imagen(conversacion.sesion_id, media_id, caption)
        else:
            resultado_envio = await whatsapp_client.enviar_documento(
                conversacion.sesion_id, media_id, filename, caption
            )

        if "error" in resultado_envio:
            logger.warning(
                "Mensaje de agente (adjunto) guardado pero no se pudo enviar por WhatsApp (conversacion_id=%s): %s",
                conversacion_id,
                resultado_envio["error"],
            )

        return mensaje


respuesta_agente_service = RespuestaAgenteService()
