from app.services.openai_client import openai_client

KEYWORDS: dict[str, list[str]] = {
    "menu": ["menu", "volver", "inicio", "hola", "buenas", "buenos dias"],
    "catalogo_general": ["catalogo general", "todos los productos", "todo el catalogo"],
    "catalogo": ["catalogo", "productos", "precio", "precios", "tienes", "venden"],
    "horario": ["horario", "horarios", "hora", "abierto", "atienden"],
    "ubicacion": ["ubicacion", "direccion", "donde", "lugar", "local", "mapa"],
    "soporte": ["soporte", "ayuda", "asesor", "reclamo"],
}

MENSAJE_BIENVENIDA = "👋 Hola, soy el asistente virtual. ¿En qué puedo ayudarte?"

OPCIONES_MENU = [
    "📍 Ver catálogo por agencia",
    "🌐 Ver catálogo general",
    "⏰ Horario",
    "📌 Ubicación",
    "🆘 Soporte",
]

OPCION_MENU_PRINCIPAL = "🔙 Menú principal"

MENSAJE_HORARIO = "⏰ Nuestro horario de atención es de Lunes a Sábado de 8:00 a 20:00."

MENSAJE_UBICACION = "📍 Nos encontramos en Av. Principal #123. También puedes ubicarnos en Google Maps buscando nuestro nombre."

MENSAJE_SOPORTE = (
    "👨‍💼 Un asesor te atenderá en breve. También puedes contactarnos al +591 70000000 "
    "o escribiendo a soporte@negocio.com."
)

MENSAJE_ERROR_SERVICIO = "⚠️ Lo sentimos, no pudimos completar tu solicitud. Intenta de nuevo en unos minutos."


def normalizar(texto: str) -> str:
    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
    texto = texto.strip().lower()
    for acentuada, simple in reemplazos.items():
        texto = texto.replace(acentuada, simple)
    return texto


def detectar_intent_por_keywords(texto: str) -> str | None:
    texto_normalizado = normalizar(texto)
    for intent, palabras in KEYWORDS.items():
        if any(palabra in texto_normalizado for palabra in palabras):
            return intent
    return None


async def detectar_intent(texto: str) -> str | None:
    intent = detectar_intent_por_keywords(texto)
    if intent:
        return intent

    return await openai_client.clasificar_intent(texto)
