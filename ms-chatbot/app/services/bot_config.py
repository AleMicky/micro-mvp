from app.services.openai_client import openai_client

KEYWORDS: dict[str, list[str]] = {
    "menu": ["menu", "volver", "inicio", "hola", "buenas", "buenos dias"],
    "carrito": ["carrito", "mi pedido", "mi carrito", "ver carrito", "confirmar pedido", "confirmar"],
    "catalogo_general": ["catalogo general", "todos los productos", "todo el catalogo", "catalogo completo"],
    "catalogo": ["catalogo", "productos", "precio", "precios", "tienes", "venden", "ofertas", "ofertas por agencia"],
    "horario": ["horario", "horarios", "hora", "abierto", "atienden"],
    "ubicacion": ["ubicacion", "direccion", "donde", "lugar", "local", "mapa", "agencias", "nuestras agencias"],
    "soporte": ["soporte", "ayuda", "asesor", "reclamo", "hablar con un asesor"],
}

MENSAJE_BIENVENIDA = (
    "👋🛍️ ¡Hola! Bienvenido a *Abuelita Serafina SuperMarket*.\n"
    "Tenemos productos de calidad al mejor precio, listos para ti. "
    "¿Qué te gustaría ver hoy? 😊"
)

OPCIONES_MENU = [
    "🛒 Ver ofertas por agencia",
    "🌐 Ver catálogo completo",
    "⏰ Horario de atención",
    "📌 Nuestras agencias",
    "🆘 Hablar con un asesor",
]

OPCION_MENU_PRINCIPAL = "🔙 Menú principal"

MENSAJE_HORARIO = (
    "⏰ ¡Te esperamos! Todas nuestras agencias atienden de Lunes a Sábado de 8:00 a 20:00.\n"
    "Ven cuando quieras, siempre tenemos algo bueno para ti. 🛍️"
)

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
