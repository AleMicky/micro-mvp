import json
import logging
from collections.abc import Awaitable, Callable

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

INTENTS_VALIDOS = ["menu", "catalogo", "catalogo_general", "horario", "ubicacion", "soporte"]

_SYSTEM_PROMPT = (
    "Eres un clasificador de intenciones para un chatbot de atención al cliente. "
    "Dado un mensaje de un cliente, clasifícalo en una de estas categorías:\n"
    "- menu: quiere volver al menú principal o saludo inicial\n"
    "- catalogo: quiere ver el catálogo de una agencia/sucursal específica\n"
    "- catalogo_general: quiere ver todo el catálogo general, sin elegir agencia\n"
    "- horario: pregunta por el horario de atención\n"
    "- ubicacion: pregunta por la dirección o ubicación del negocio\n"
    "- soporte: quiere hablar con un asesor o tiene un problema/reclamo\n"
    "Si el mensaje es una pregunta libre sobre productos específicos (ej. '¿tienen arroz?', "
    "'¿cuánto cuesta X?'), o no corresponde claramente a ninguna categoría, responde null."
)

_SYSTEM_PROMPT_VENDEDOR = (
    "Eres el vendedor virtual de atención al cliente de un negocio por WhatsApp. "
    "Responde de forma breve, amable y natural en español, como lo haría un vendedor real. "
    "Cuando el cliente pregunte por productos específicos, precios o disponibilidad, usa las "
    "herramientas disponibles (buscar_productos, consultar_stock, listar_categorias_disponibles) "
    "para consultar información real del sistema antes de responder — nunca inventes precios, "
    "nombres de productos ni disponibilidad. Si un producto no tiene precio configurado, dilo "
    "explícitamente en vez de inventar uno. Si te preguntan qué eres, explica que eres un "
    "asistente virtual que ayuda con el catálogo, horarios, ubicación y soporte. "
    "Termina invitando a escribir 'menu' para ver las opciones disponibles. "
    "Responde en máximo 4 oraciones."
)

_RESPONSE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "clasificacion_intent",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": ["string", "null"],
                    "enum": [*INTENTS_VALIDOS, None],
                }
            },
            "required": ["intent"],
            "additionalProperties": False,
        },
    },
}

_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_productos",
            "description": "Busca productos del catálogo por nombre o descripción. Devuelve hasta 5 coincidencias con su precio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Texto a buscar, ej. 'arroz' o 'cable hdmi'"}
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_stock",
            "description": "Consulta el stock consolidado (todas las agencias) de un producto por su ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto_id": {"type": "integer", "description": "ID del producto a consultar"}
                },
                "required": ["producto_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_categorias_disponibles",
            "description": "Lista las categorías de productos disponibles en el catálogo.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
]

EjecutorTool = Callable[..., Awaitable[dict | list]]

_MAX_RONDAS_TOOLS = 2


class OpenAIClient:
    async def clasificar_intent(self, texto: str) -> str | None:
        if not settings.openai_api_key:
            return None

        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": texto},
            ],
            "response_format": _RESPONSE_SCHEMA,
            "max_tokens": 20,
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                logger.warning("Error clasificando intent con OpenAI (%s): %s", response.status_code, response.text)
                return None

            data = response.json()
            contenido = json.loads(data["choices"][0]["message"]["content"])
            intent = contenido.get("intent")
            return intent if intent in INTENTS_VALIDOS else None
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning("Error clasificando intent con OpenAI: %s", exc)
            return None

    async def responder_como_vendedor(self, texto: str, ejecutores: dict[str, EjecutorTool]) -> str | None:
        if not settings.openai_api_key:
            return None

        messages: list[dict] = [
            {"role": "system", "content": _SYSTEM_PROMPT_VENDEDOR},
            {"role": "user", "content": texto},
        ]

        try:
            for _ in range(_MAX_RONDAS_TOOLS):
                data = await self._chat_completion(messages, con_tools=True)
                if data is None:
                    return None

                mensaje = data["choices"][0]["message"]
                tool_calls = mensaje.get("tool_calls")
                if not tool_calls:
                    return mensaje.get("content", "").strip() or None

                messages.append(mensaje)
                for tool_call in tool_calls:
                    resultado = await self._ejecutar_tool_call(tool_call, ejecutores)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(resultado, ensure_ascii=False),
                        }
                    )

            data = await self._chat_completion(messages, con_tools=False)
            if data is None:
                return None
            return data["choices"][0]["message"].get("content", "").strip() or None
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning("Error en conversación con OpenAI: %s", exc)
            return None

    async def _chat_completion(self, messages: list[dict], con_tools: bool) -> dict | None:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload: dict = {"model": settings.openai_model, "messages": messages, "max_tokens": 300}
        if con_tools:
            payload["tools"] = _TOOLS
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code >= 400:
            logger.warning("Error en chat completion con OpenAI (%s): %s", response.status_code, response.text)
            return None
        return response.json()

    async def _ejecutar_tool_call(self, tool_call: dict, ejecutores: dict[str, EjecutorTool]) -> dict | list:
        nombre = tool_call["function"]["name"]
        try:
            args = json.loads(tool_call["function"]["arguments"])
        except (json.JSONDecodeError, KeyError):
            args = {}

        ejecutor = ejecutores.get(nombre)
        if not ejecutor:
            return {"error": f"Herramienta desconocida: {nombre}"}

        try:
            return await ejecutor(**args)
        except Exception as exc:
            logger.warning("Error ejecutando tool %s: %s", nombre, exc)
            return {"error": "No se pudo completar la consulta"}


openai_client = OpenAIClient()
