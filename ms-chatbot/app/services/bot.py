from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversacion import ChatbotConversacion
from app.services import bot_config
from app.services.catalogos import catalogos_client
from app.services.company import company_client
from app.services.conversacion import conversacion_service
from app.services.inventario import inventario_client


@dataclass
class ResultadoBot:
    respuesta: str
    opciones: list[str] | None
    nuevo_estado: str
    nuevo_contexto: dict


def resolver_seleccion(texto: str, opciones: list[dict]) -> dict | None:
    texto_normalizado = bot_config.normalizar(texto)

    if texto_normalizado.isdigit():
        indice = int(texto_normalizado) - 1
        if 0 <= indice < len(opciones):
            return opciones[indice]
        return None

    for opcion in opciones:
        if texto_normalizado in bot_config.normalizar(opcion["nombre"]):
            return opcion
    return None


async def handle_menu(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    return ResultadoBot(
        respuesta=bot_config.MENSAJE_BIENVENIDA,
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={},
    )


async def handle_horario(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    return ResultadoBot(
        respuesta=bot_config.MENSAJE_HORARIO,
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={},
    )


async def handle_ubicacion(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    return ResultadoBot(
        respuesta=bot_config.MENSAJE_UBICACION,
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={},
    )


async def handle_soporte(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    return ResultadoBot(
        respuesta=bot_config.MENSAJE_SOPORTE,
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="soporte",
        nuevo_contexto={},
    )


async def handle_agencias(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    agencias_contexto = conversacion.contexto.get("agencias") if conversacion.estado == "agencias" else None

    if agencias_contexto:
        seleccion = resolver_seleccion(texto, agencias_contexto)
        if seleccion:
            return await _mostrar_categorias(seleccion["id"], seleccion["nombre"])

    almacenes = await inventario_client.listar_almacenes()
    if not almacenes:
        return ResultadoBot(
            respuesta="Por el momento no tenemos agencias disponibles.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={},
        )

    sucursales = await company_client.listar_sucursales()
    nombres_sucursal = {s["id"]: s["nombre"] for s in sucursales}

    opciones_contexto = [
        {
            "id": almacen["id"],
            "nombre": nombres_sucursal.get(almacen.get("sucursal_id"), almacen["nombre"]),
        }
        for almacen in almacenes
    ]
    nombres = [a["nombre"] for a in opciones_contexto]
    return ResultadoBot(
        respuesta="Selecciona una agencia escribiendo su número o nombre:",
        opciones=nombres,
        nuevo_estado="agencias",
        nuevo_contexto={"agencias": opciones_contexto},
    )


async def _mostrar_categorias(almacen_id: int, agencia_nombre: str) -> ResultadoBot:
    categorias = await catalogos_client.listar_categorias()
    if not categorias:
        return ResultadoBot(
            respuesta="Por el momento no tenemos categorías disponibles.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={},
        )

    opciones_contexto = [{"id": c["id"], "nombre": c["nombre"]} for c in categorias]
    nombres = [c["nombre"] for c in opciones_contexto]
    return ResultadoBot(
        respuesta=f"Agencia {agencia_nombre}.\nSelecciona una categoría escribiendo su número o nombre:",
        opciones=nombres,
        nuevo_estado="catalogo_categorias",
        nuevo_contexto={
            "categorias": opciones_contexto,
            "almacen_id": almacen_id,
            "agencia_nombre": agencia_nombre,
        },
    )


async def handle_catalogo_categorias(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    categorias_contexto = conversacion.contexto.get("categorias") if conversacion.estado == "catalogo_categorias" else None
    almacen_id = conversacion.contexto.get("almacen_id")
    agencia_nombre = conversacion.contexto.get("agencia_nombre", "")

    if categorias_contexto and almacen_id is not None:
        seleccion = resolver_seleccion(texto, categorias_contexto)
        if seleccion:
            return await _mostrar_productos(almacen_id, agencia_nombre, seleccion["id"], seleccion["nombre"])

    return await handle_agencias(conversacion, texto)


async def _mostrar_productos(
    almacen_id: int, agencia_nombre: str, categoria_id: int, categoria_nombre: str
) -> ResultadoBot:
    productos = await catalogos_client.listar_productos()
    productos_categoria = [p for p in productos if p.get("categoria_id") == categoria_id]

    if not productos_categoria:
        return ResultadoBot(
            respuesta=f"No hay productos disponibles en la categoría {categoria_nombre}.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={},
        )

    existencias = await inventario_client.listar_existencias_por_almacen(almacen_id)
    stock_por_producto = {e["producto_id"]: float(e["cantidad_actual"]) for e in existencias}

    opciones_contexto = []
    lineas = [f"Productos de {categoria_nombre} en {agencia_nombre}:"]
    for producto in productos_categoria:
        cantidad = stock_por_producto.get(producto["id"], 0.0)
        precio = producto.get("precio_actual")
        precio_texto = f"Bs. {precio}" if precio is not None else "Precio no disponible"
        lineas.append(f"- {producto['nombre']}: {precio_texto} | Stock: {int(cantidad)}")
        opciones_contexto.append(
            {"id": producto["id"], "nombre": producto["nombre"], "categoria_id": categoria_id}
        )

    return ResultadoBot(
        respuesta="\n".join(lineas) + "\n\nEscribe el número o nombre del producto para ver el detalle.",
        opciones=[p["nombre"] for p in opciones_contexto],
        nuevo_estado="catalogo_productos",
        nuevo_contexto={
            "productos": opciones_contexto,
            "categoria_id": categoria_id,
            "categoria_nombre": categoria_nombre,
            "almacen_id": almacen_id,
            "agencia_nombre": agencia_nombre,
        },
    )


async def handle_catalogo_productos(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    productos_contexto = conversacion.contexto.get("productos", [])
    almacen_id = conversacion.contexto.get("almacen_id")
    agencia_nombre = conversacion.contexto.get("agencia_nombre", "")

    seleccion = resolver_seleccion(texto, productos_contexto)
    if not seleccion:
        return ResultadoBot(
            respuesta="No reconocí ese producto. Escribe el número o nombre de la lista.",
            opciones=[p["nombre"] for p in productos_contexto],
            nuevo_estado="catalogo_productos",
            nuevo_contexto=conversacion.contexto,
        )

    return await _mostrar_detalle_producto(
        almacen_id, agencia_nombre, seleccion["id"], seleccion["categoria_id"]
    )


async def _mostrar_detalle_producto(
    almacen_id: int, agencia_nombre: str, producto_id: int, categoria_id: int
) -> ResultadoBot:
    producto = await catalogos_client.obtener_producto(producto_id)
    existencias = await inventario_client.listar_existencias_por_almacen(almacen_id)
    cantidad = next(
        (float(e["cantidad_actual"]) for e in existencias if e["producto_id"] == producto_id), 0.0
    )

    disponibilidad = "Disponible" if cantidad > 5 else f"Últimas {int(cantidad)} unidades" if cantidad > 0 else "Sin stock"
    precio = producto.get("precio_actual")
    precio_texto = f"Bs. {precio}" if precio is not None else "Precio no disponible"

    lineas = [
        f"{producto['nombre']}",
        f"Agencia: {agencia_nombre}",
        f"Precio: {precio_texto}",
        f"Stock: {disponibilidad}",
    ]
    if producto.get("descripcion"):
        lineas.append(f"Descripción: {producto['descripcion']}")

    return ResultadoBot(
        respuesta="\n".join(lineas),
        opciones=["Ver más productos", "Menú principal"],
        nuevo_estado="producto_detalle",
        nuevo_contexto={
            "producto_id": producto_id,
            "categoria_id": categoria_id,
            "almacen_id": almacen_id,
            "agencia_nombre": agencia_nombre,
        },
    )


async def handle_producto_detalle(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    texto_normalizado = bot_config.normalizar(texto)
    almacen_id = conversacion.contexto.get("almacen_id")
    agencia_nombre = conversacion.contexto.get("agencia_nombre", "")
    categoria_id = conversacion.contexto.get("categoria_id")

    if "ver mas" in texto_normalizado or "mas productos" in texto_normalizado:
        if almacen_id is not None and categoria_id is not None:
            return await _mostrar_productos(almacen_id, agencia_nombre, categoria_id, "la categoría seleccionada")
        return await handle_agencias(conversacion, texto)

    return await handle_menu(conversacion, texto)


STATE_HANDLERS = {
    "menu": handle_menu,
    "agencias": handle_agencias,
    "catalogo_categorias": handle_catalogo_categorias,
    "catalogo_productos": handle_catalogo_productos,
    "producto_detalle": handle_producto_detalle,
    "soporte": handle_soporte,
}

INTENT_HANDLERS = {
    "menu": handle_menu,
    "horario": handle_horario,
    "ubicacion": handle_ubicacion,
    "soporte": handle_soporte,
    "catalogo": handle_agencias,
}


def _es_opcion_de_estado_actual(conversacion: ChatbotConversacion, texto: str) -> bool:
    texto_normalizado = bot_config.normalizar(texto)
    if conversacion.estado == "producto_detalle":
        return "ver mas" in texto_normalizado or "mas productos" in texto_normalizado or "menu" in texto_normalizado
    return False


async def procesar_mensaje(db: AsyncSession, sesion_id: str, texto: str) -> ResultadoBot:
    conversacion = await conversacion_service.get_or_create(db, sesion_id)

    if _es_opcion_de_estado_actual(conversacion, texto):
        handler = STATE_HANDLERS[conversacion.estado]
    else:
        intent = bot_config.detectar_intent(texto)
        if intent:
            handler = INTENT_HANDLERS[intent]
        else:
            handler = STATE_HANDLERS.get(conversacion.estado, handle_menu)

    resultado = await handler(conversacion, texto)

    if resultado.nuevo_estado != "menu" and resultado.opciones:
        if bot_config.OPCION_MENU_PRINCIPAL not in resultado.opciones:
            resultado.opciones = [*resultado.opciones, bot_config.OPCION_MENU_PRINCIPAL]

    await conversacion_service.actualizar_estado(
        db, conversacion, resultado.nuevo_estado, resultado.nuevo_contexto
    )
    return resultado
