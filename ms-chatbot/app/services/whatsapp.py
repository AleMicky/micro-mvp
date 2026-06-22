import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


MAX_FILAS_LISTA = 10
MAX_LARGO_TITULO_FILA = 24


class WhatsAppClient:
    def _url_mensajes(self) -> str:
        return (
            f"https://graph.facebook.com/{settings.whatsapp_api_version}"
            f"/{settings.whatsapp_phone_number_id}/messages"
        )

    def _url_media(self) -> str:
        return (
            f"https://graph.facebook.com/{settings.whatsapp_api_version}"
            f"/{settings.whatsapp_phone_number_id}/media"
        )

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {settings.whatsapp_access_token}"}

    async def subir_media(self, contenido: bytes, mime_type: str, filename: str) -> str | None:
        files = {"file": (filename, contenido, mime_type)}
        data = {"messaging_product": "whatsapp", "type": mime_type}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self._url_media(), headers=self._headers(), data=data, files=files
                )
            if response.status_code >= 400:
                logger.warning("Error subiendo media a WhatsApp (%s): %s", response.status_code, response.text)
                return None
            return response.json().get("id")
        except httpx.HTTPError as exc:
            logger.warning("Error subiendo media a WhatsApp: %s", exc)
            return None

    async def _enviar(self, payload: dict) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self._url_mensajes(), headers=self._headers(), json=payload)
            if response.status_code >= 400:
                logger.warning("Error enviando mensaje a WhatsApp (%s): %s", response.status_code, response.text)
                return {"error": response.text}
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning("Error enviando mensaje a WhatsApp: %s", exc)
            return {"error": str(exc)}

    async def marcar_como_leido_con_typing(self, message_id: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
            "typing_indicator": {"type": "text"},
        }
        return await self._enviar(payload)

    async def enviar_texto(self, to: str, mensaje: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": mensaje, "preview_url": False},
        }
        return await self._enviar(payload)

    async def enviar_imagen(self, to: str, media_id: str, caption: str | None = None) -> dict:
        image_payload: dict = {"id": media_id}
        if caption:
            image_payload["caption"] = caption
        payload = {"messaging_product": "whatsapp", "to": to, "type": "image", "image": image_payload}
        return await self._enviar(payload)

    async def enviar_documento(self, to: str, media_id: str, filename: str, caption: str | None = None) -> dict:
        document_payload: dict = {"id": media_id, "filename": filename}
        if caption:
            document_payload["caption"] = caption
        payload = {"messaging_product": "whatsapp", "to": to, "type": "document", "document": document_payload}
        return await self._enviar(payload)

    async def enviar_lista(self, to: str, mensaje: str, opciones: list[str], boton: str = "Ver opciones") -> dict:
        visibles = opciones[:MAX_FILAS_LISTA]
        restantes = opciones[MAX_FILAS_LISTA:]

        texto_body = mensaje
        if restantes:
            texto_body += "\n\nTambién disponibles (escribe el nombre): " + ", ".join(restantes)

        filas = [
            {"id": f"opcion_{i}", "title": opcion[:MAX_LARGO_TITULO_FILA]}
            for i, opcion in enumerate(visibles)
        ]
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": texto_body},
                "action": {
                    "button": boton,
                    "sections": [{"title": "Opciones", "rows": filas}],
                },
            },
        }
        return await self._enviar(payload)


whatsapp_client = WhatsAppClient()
