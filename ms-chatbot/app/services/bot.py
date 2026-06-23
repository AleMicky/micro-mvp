from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.conversacion import ChatbotConversacion
from app.services import bot_config
from app.services.catalogos import catalogos_client
from app.services.company import company_client
from app.services.conversacion import conversacion_service
from app.services.inventario import inventario_client
from app.services.openai_client import openai_client
from app.services.pdf_pedido import generar_pdf_pedido
from app.services.ventas import ventas_client


@dataclass
class ResultadoBot:
    respuesta: str
    opciones: list[str] | None
    nuevo_estado: str
    nuevo_contexto: dict
    pdf_pendiente: bytes | None = None
    pdf_nombre: str | None = None
    ubicaciones_pendientes: list[dict] | None = None
    enviar_logo: bool = False


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
    carrito = conversacion.contexto.get("carrito")
    return ResultadoBot(
        respuesta=bot_config.MENSAJE_BIENVENIDA,
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={"carrito": carrito} if carrito else {},
    )


async def _tool_buscar_productos(query: str) -> list[dict]:
    productos = await catalogos_client.listar_productos()
    query_normalizado = bot_config.normalizar(query)
    coincidencias = [
        p
        for p in productos
        if query_normalizado in bot_config.normalizar(p.get("nombre", ""))
        or query_normalizado in bot_config.normalizar(p.get("descripcion") or "")
    ]
    return [
        {
            "id": p["id"],
            "nombre": p["nombre"],
            "descripcion": p.get("descripcion"),
            "precio_actual": p.get("precio_actual"),
        }
        for p in coincidencias[:5]
    ]


async def _tool_consultar_stock(producto_id: int) -> dict:
    stock = await inventario_client.obtener_stock(producto_id)
    return {"cantidad_total": stock.get("cantidad_total", 0)}


async def _tool_listar_categorias_disponibles() -> list[dict]:
    categorias = await catalogos_client.listar_categorias()
    return [{"nombre": c["nombre"]} for c in categorias]


_TOOL_EJECUTORES = {
    "buscar_productos": _tool_buscar_productos,
    "consultar_stock": _tool_consultar_stock,
    "listar_categorias_disponibles": _tool_listar_categorias_disponibles,
}


async def handle_vendedor_ia(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    respuesta = await openai_client.responder_como_vendedor(texto, _TOOL_EJECUTORES)
    if not respuesta:
        return await handle_menu(conversacion, texto)

    carrito = conversacion.contexto.get("carrito")
    return ResultadoBot(
        respuesta=respuesta,
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={"carrito": carrito} if carrito else {},
    )


async def handle_horario(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    carrito = conversacion.contexto.get("carrito")
    return ResultadoBot(
        respuesta=bot_config.MENSAJE_HORARIO,
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={"carrito": carrito} if carrito else {},
        enviar_logo=True,
    )


async def handle_ubicacion(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    carrito = conversacion.contexto.get("carrito")
    almacenes = await inventario_client.listar_almacenes()

    ubicaciones = [
        {
            "latitud": float(a["latitud"]),
            "longitud": float(a["longitud"]),
            "nombre": a.get("nombre", ""),
            "direccion": a.get("direccion") or "",
        }
        for a in almacenes
        if a.get("latitud") is not None and a.get("longitud") is not None
    ]

    if not ubicaciones:
        return ResultadoBot(
            respuesta=bot_config.MENSAJE_UBICACION,
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={"carrito": carrito} if carrito else {},
            enviar_logo=True,
        )

    return ResultadoBot(
        respuesta="📍 Estas son nuestras agencias:",
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={"carrito": carrito} if carrito else {},
        ubicaciones_pendientes=ubicaciones,
        enviar_logo=True,
    )


async def handle_soporte(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    carrito = conversacion.contexto.get("carrito")
    return ResultadoBot(
        respuesta=bot_config.MENSAJE_SOPORTE,
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="soporte",
        nuevo_contexto={"carrito": carrito} if carrito else {},
    )


async def handle_agencias(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    agencias_contexto = conversacion.contexto.get("agencias") if conversacion.estado == "agencias" else None
    carrito = conversacion.contexto.get("carrito")

    if agencias_contexto:
        seleccion = resolver_seleccion(texto, agencias_contexto)
        if seleccion:
            return await _mostrar_categorias(seleccion["id"], seleccion["nombre"], carrito)

    almacenes = await inventario_client.listar_almacenes()
    if not almacenes:
        return ResultadoBot(
            respuesta="❌ Por el momento no tenemos agencias disponibles.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={"carrito": carrito} if carrito else {},
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
        respuesta="🏬 Selecciona una agencia escribiendo su número o nombre:",
        opciones=nombres,
        nuevo_estado="agencias",
        nuevo_contexto={"agencias": opciones_contexto, "carrito": carrito},
    )


async def _mostrar_categorias(almacen_id: int, agencia_nombre: str, carrito: dict | None = None) -> ResultadoBot:
    categorias = await catalogos_client.listar_categorias()
    if not categorias:
        return ResultadoBot(
            respuesta="❌ Por el momento no tenemos categorías disponibles.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={"carrito": carrito} if carrito else {},
        )

    opciones_contexto = [{"id": c["id"], "nombre": c["nombre"]} for c in categorias]
    nombres = [c["nombre"] for c in opciones_contexto]
    return ResultadoBot(
        respuesta=f"🏬 Agencia {agencia_nombre}.\n🗂️ Selecciona una categoría escribiendo su número o nombre:",
        opciones=nombres,
        nuevo_estado="catalogo_categorias",
        nuevo_contexto={
            "categorias": opciones_contexto,
            "almacen_id": almacen_id,
            "agencia_nombre": agencia_nombre,
            "carrito": carrito,
        },
    )


async def handle_catalogo_categorias(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    categorias_contexto = conversacion.contexto.get("categorias") if conversacion.estado == "catalogo_categorias" else None
    almacen_id = conversacion.contexto.get("almacen_id")
    agencia_nombre = conversacion.contexto.get("agencia_nombre", "")
    carrito = conversacion.contexto.get("carrito")

    if categorias_contexto and almacen_id is not None:
        seleccion = resolver_seleccion(texto, categorias_contexto)
        if seleccion:
            return await _mostrar_productos(almacen_id, agencia_nombre, seleccion["id"], seleccion["nombre"], carrito)

    return await handle_agencias(conversacion, texto)


async def _mostrar_productos(
    almacen_id: int, agencia_nombre: str, categoria_id: int, categoria_nombre: str, carrito: dict | None = None
) -> ResultadoBot:
    productos = await catalogos_client.listar_productos()
    productos_categoria = [p for p in productos if p.get("categoria_id") == categoria_id]

    if not productos_categoria:
        return ResultadoBot(
            respuesta=f"❌ No hay productos disponibles en la categoría {categoria_nombre}.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={"carrito": carrito} if carrito else {},
        )

    existencias = await inventario_client.listar_existencias_por_almacen(almacen_id)
    stock_por_producto = {e["producto_id"]: float(e["cantidad_actual"]) for e in existencias}

    opciones_contexto = []
    lineas = [f"📦 Productos de {categoria_nombre} en {agencia_nombre}:"]
    for producto in productos_categoria:
        cantidad = stock_por_producto.get(producto["id"], 0.0)
        precio = producto.get("precio_actual")
        precio_texto = f"Bs. {precio}" if precio is not None else "Precio no disponible"
        lineas.append(
            f"• {producto['nombre']} — 💰 {precio_texto} | 📦 Stock: {int(cantidad)}"
        )
        opciones_contexto.append(
            {"id": producto["id"], "nombre": producto["nombre"], "categoria_id": categoria_id}
        )

    return ResultadoBot(
        respuesta="\n".join(lineas) + "\n\n✍️ Escribe el número o nombre del producto para ver el detalle.",
        opciones=[p["nombre"] for p in opciones_contexto],
        nuevo_estado="catalogo_productos",
        nuevo_contexto={
            "productos": opciones_contexto,
            "categoria_id": categoria_id,
            "categoria_nombre": categoria_nombre,
            "almacen_id": almacen_id,
            "agencia_nombre": agencia_nombre,
            "carrito": carrito,
        },
    )


async def handle_catalogo_productos(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    productos_contexto = conversacion.contexto.get("productos", [])
    almacen_id = conversacion.contexto.get("almacen_id")
    agencia_nombre = conversacion.contexto.get("agencia_nombre", "")
    carrito = conversacion.contexto.get("carrito")

    seleccion = resolver_seleccion(texto, productos_contexto)
    if not seleccion:
        return ResultadoBot(
            respuesta="❌ No reconocí ese producto. Escribe el número o nombre de la lista.",
            opciones=[p["nombre"] for p in productos_contexto],
            nuevo_estado="catalogo_productos",
            nuevo_contexto=conversacion.contexto,
        )

    return await _mostrar_detalle_producto(
        almacen_id, agencia_nombre, seleccion["id"], seleccion["categoria_id"], carrito
    )


async def _mostrar_detalle_producto(
    almacen_id: int, agencia_nombre: str, producto_id: int, categoria_id: int, carrito: dict | None = None
) -> ResultadoBot:
    producto = await catalogos_client.obtener_producto(producto_id)
    existencias = await inventario_client.listar_existencias_por_almacen(almacen_id)
    cantidad = next(
        (float(e["cantidad_actual"]) for e in existencias if e["producto_id"] == producto_id), 0.0
    )

    disponibilidad = "🟢 Disponible" if cantidad > 5 else f"⚠️ Últimas {int(cantidad)} unidades" if cantidad > 0 else "❌ Sin stock"
    precio = producto.get("precio_actual")
    precio_texto = f"Bs. {precio}" if precio is not None else "Precio no disponible"

    lineas = [
        f"📦 {producto['nombre']}",
        f"🏷️ Agencia: {agencia_nombre}",
        f"💰 Precio: {precio_texto}",
        f"📊 Stock: {disponibilidad}",
    ]
    if producto.get("descripcion"):
        lineas.append(f"📝 Descripción: {producto['descripcion']}")

    opciones = ["🔎 Ver más productos", "🔙 Menú principal"]
    if cantidad > 0:
        opciones.insert(0, "🛒 Agregar al carrito")

    return ResultadoBot(
        respuesta="\n".join(lineas),
        opciones=opciones,
        nuevo_estado="producto_detalle",
        nuevo_contexto={
            "producto_id": producto_id,
            "categoria_id": categoria_id,
            "almacen_id": almacen_id,
            "agencia_nombre": agencia_nombre,
            "carrito": carrito,
        },
    )


async def handle_producto_detalle(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    texto_normalizado = bot_config.normalizar(texto)
    almacen_id = conversacion.contexto.get("almacen_id")
    agencia_nombre = conversacion.contexto.get("agencia_nombre", "")
    categoria_id = conversacion.contexto.get("categoria_id")
    carrito = conversacion.contexto.get("carrito")

    if "agregar" in texto_normalizado or "carrito" in texto_normalizado:
        return await _iniciar_agregar_carrito(conversacion)

    if "ver mas" in texto_normalizado or "mas productos" in texto_normalizado:
        if almacen_id is not None and categoria_id is not None:
            return await _mostrar_productos(almacen_id, agencia_nombre, categoria_id, "la categoría seleccionada", carrito)
        return await handle_agencias(conversacion, texto)

    return ResultadoBot(
        respuesta="🔙 Volviendo al menú principal...",
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={"carrito": carrito} if carrito else {},
    )


async def _iniciar_agregar_carrito(conversacion: ChatbotConversacion) -> ResultadoBot:
    producto_id = conversacion.contexto.get("producto_id")
    almacen_id = conversacion.contexto.get("almacen_id")
    agencia_nombre = conversacion.contexto.get("agencia_nombre", "")
    carrito = conversacion.contexto.get("carrito")

    if carrito and carrito.get("almacen_id") != almacen_id:
        return ResultadoBot(
            respuesta=(
                f"⚠️ Ya tienes productos en el carrito de {carrito.get('agencia_nombre')}. "
                "Escribe 'carrito' para verlo y vaciarlo antes de agregar de otra agencia."
            ),
            opciones=["🛒 Ver carrito", "🔙 Menú principal"],
            nuevo_estado="menu",
            nuevo_contexto={"carrito": carrito},
        )

    producto = await catalogos_client.obtener_producto(producto_id)
    existencias = await inventario_client.listar_existencias_por_almacen(almacen_id)
    stock = next(
        (float(e["cantidad_actual"]) for e in existencias if e["producto_id"] == producto_id), 0.0
    )
    if stock <= 0:
        return ResultadoBot(
            respuesta=f"❌ Lo sentimos, {producto['nombre']} no tiene stock disponible en {agencia_nombre} en este momento.",
            opciones=["🔎 Ver más productos", "🔙 Menú principal"],
            nuevo_estado="menu",
            nuevo_contexto={"carrito": carrito} if carrito else {},
        )

    precio = producto.get("precio_actual")
    return ResultadoBot(
        respuesta=f"🛒 ¿Cuántas unidades de *{producto['nombre']}* deseas agregar? Escribe solo el número.",
        opciones=None,
        nuevo_estado="producto_cantidad",
        nuevo_contexto={
            "carrito": carrito,
            "producto_pendiente": {
                "producto_id": producto_id,
                "nombre": producto["nombre"],
                "precio_unitario": float(precio) if precio is not None else 0.0,
            },
            "almacen_id": almacen_id,
            "agencia_nombre": agencia_nombre,
            "categoria_id": conversacion.contexto.get("categoria_id"),
        },
    )


_PALABRAS_CANCELAR = ("menu", "cancelar", "salir", "no quiero", "nada", "no gracias")


async def handle_producto_cantidad(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    texto_normalizado = bot_config.normalizar(texto)
    pendiente = conversacion.contexto.get("producto_pendiente")
    almacen_id = conversacion.contexto.get("almacen_id")
    agencia_nombre = conversacion.contexto.get("agencia_nombre", "")
    carrito = conversacion.contexto.get("carrito")

    if not pendiente or any(p in texto_normalizado for p in _PALABRAS_CANCELAR):
        resultado = await handle_menu(conversacion, texto)
        if carrito:
            resultado.nuevo_contexto["carrito"] = carrito
        return resultado

    if not texto_normalizado.isdigit() or int(texto_normalizado) <= 0:
        return ResultadoBot(
            respuesta="❌ Escribe solo un número entero mayor a 0, ej. 2 (o escribe 'cancelar' para salir)",
            opciones=None,
            nuevo_estado="producto_cantidad",
            nuevo_contexto=conversacion.contexto,
        )

    cantidad = int(texto_normalizado)
    existencias = await inventario_client.listar_existencias_por_almacen(almacen_id)
    stock = next(
        (float(e["cantidad_actual"]) for e in existencias if e["producto_id"] == pendiente["producto_id"]), 0.0
    )

    if stock <= 0:
        resultado = await handle_menu(conversacion, texto)
        resultado.respuesta = f"❌ Lo sentimos, {pendiente['nombre']} no tiene stock disponible en este momento."
        if carrito:
            resultado.nuevo_contexto["carrito"] = carrito
        return resultado

    if cantidad > stock:
        return ResultadoBot(
            respuesta=f"⚠️ Solo hay {int(stock)} unidades disponibles de {pendiente['nombre']}. Escribe otra cantidad (o 'cancelar' para salir).",
            opciones=None,
            nuevo_estado="producto_cantidad",
            nuevo_contexto=conversacion.contexto,
        )

    carrito = _agregar_item_carrito(carrito, almacen_id, agencia_nombre, pendiente, cantidad)
    return ResultadoBot(
        respuesta=f"✅ Agregado: {cantidad} x {pendiente['nombre']}.\n\n{_formatear_resumen_carrito(carrito)}",
        opciones=["🛍️ Seguir comprando", "✅ Confirmar pedido", "🛒 Ver carrito"],
        nuevo_estado="menu",
        nuevo_contexto={"carrito": carrito},
    )


def _agregar_item_carrito(
    carrito: dict | None, almacen_id: int, agencia_nombre: str, producto: dict, cantidad: int
) -> dict:
    if not carrito:
        carrito = {"almacen_id": almacen_id, "agencia_nombre": agencia_nombre, "items": []}
    for item in carrito["items"]:
        if item["producto_id"] == producto["producto_id"]:
            item["cantidad"] += cantidad
            return carrito
    carrito["items"].append({**producto, "cantidad": cantidad})
    return carrito


def _formatear_resumen_carrito(carrito: dict) -> str:
    lineas = ["🛒 Tu carrito:"]
    total = 0.0
    for item in carrito["items"]:
        subtotal = item["precio_unitario"] * item["cantidad"]
        total += subtotal
        lineas.append(f"• {item['nombre']} x{item['cantidad']} — Bs. {subtotal:.2f}")
    lineas.append(f"\n💰 Total: Bs. {total:.2f}")
    return "\n".join(lineas)


async def handle_carrito(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    texto_normalizado = bot_config.normalizar(texto)
    carrito = conversacion.contexto.get("carrito")

    if not carrito or not carrito.get("items"):
        return ResultadoBot(
            respuesta="🛒 Tu carrito está vacío. Ve al catálogo para agregar productos.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={},
        )

    if "confirmar" in texto_normalizado:
        return await _confirmar_pedido(conversacion, carrito)

    if "vaciar" in texto_normalizado or "cancelar" in texto_normalizado:
        return ResultadoBot(
            respuesta="🗑️ Carrito vaciado.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={},
        )

    if "seguir" in texto_normalizado or "comprando" in texto_normalizado or "catalogo" in texto_normalizado:
        return await handle_agencias(conversacion, texto)

    return ResultadoBot(
        respuesta=_formatear_resumen_carrito(carrito),
        opciones=["✅ Confirmar pedido", "🗑️ Vaciar carrito", "🛍️ Seguir comprando"],
        nuevo_estado="carrito",
        nuevo_contexto={"carrito": carrito},
    )


async def _confirmar_pedido(conversacion: ChatbotConversacion, carrito: dict) -> ResultadoBot:
    detalles = [
        {"producto_id": i["producto_id"], "cantidad": i["cantidad"], "precio_unitario": i["precio_unitario"]}
        for i in carrito["items"]
    ]
    payload = {
        "cliente_id": settings.whatsapp_cliente_id,
        "almacen_id": carrito["almacen_id"],
        "estado": "PENDIENTE",
        "detalles": detalles,
        "observaciones": f"Pedido WhatsApp {conversacion.sesion_id}",
    }

    try:
        cotizacion = await ventas_client.crear_cotizacion(payload)
    except HTTPException as exc:
        detalle = exc.detail if isinstance(exc.detail, str) else "stock insuficiente o error del sistema"
        return ResultadoBot(
            respuesta=(
                f"⚠️ No pudimos generar tu cotización: {detalle}.\n"
                "Tu carrito se mantiene. Ajusta las cantidades escribiendo 'carrito' o intenta de nuevo."
            ),
            opciones=["🛒 Ver carrito", "🔙 Menú principal"],
            nuevo_estado="carrito",
            nuevo_contexto={"carrito": carrito},
        )

    pdf_bytes = generar_pdf_pedido(cotizacion, carrito, conversacion.sesion_id)
    return ResultadoBot(
        respuesta=(
            f"📋 ¡Cotización generada! Código: {cotizacion['codigo']}\n"
            f"💰 Total: Bs. {cotizacion['total']}\n"
            "📄 Te enviamos el detalle en PDF.\n"
            "Nuestro equipo de ventas la revisará y te confirmaremos en breve."
        ),
        opciones=bot_config.OPCIONES_MENU,
        nuevo_estado="menu",
        nuevo_contexto={},
        pdf_pendiente=pdf_bytes,
        pdf_nombre=f"Cotizacion_{cotizacion['codigo']}.pdf",
    )


async def handle_catalogo_general(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    categorias_contexto = (
        conversacion.contexto.get("categorias") if conversacion.estado == "catalogo_general_categorias" else None
    )
    carrito = conversacion.contexto.get("carrito")

    if categorias_contexto:
        seleccion = resolver_seleccion(texto, categorias_contexto)
        if seleccion:
            return await _mostrar_productos_general(seleccion["id"], seleccion["nombre"], carrito)

    categorias = await catalogos_client.listar_categorias()
    if not categorias:
        return ResultadoBot(
            respuesta="❌ Por el momento no tenemos categorías disponibles.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={"carrito": carrito} if carrito else {},
        )

    opciones_contexto = [{"id": c["id"], "nombre": c["nombre"]} for c in categorias]
    nombres = [c["nombre"] for c in opciones_contexto]
    return ResultadoBot(
        respuesta="🌐 Catálogo general.\nSelecciona una categoría escribiendo su número o nombre:",
        opciones=nombres,
        nuevo_estado="catalogo_general_categorias",
        nuevo_contexto={"categorias": opciones_contexto, "carrito": carrito},
    )


async def _mostrar_productos_general(categoria_id: int, categoria_nombre: str, carrito: dict | None = None) -> ResultadoBot:
    productos = await catalogos_client.listar_productos()
    productos_categoria = [p for p in productos if p.get("categoria_id") == categoria_id]

    if not productos_categoria:
        return ResultadoBot(
            respuesta=f"❌ No hay productos disponibles en la categoría {categoria_nombre}.",
            opciones=bot_config.OPCIONES_MENU,
            nuevo_estado="menu",
            nuevo_contexto={"carrito": carrito} if carrito else {},
        )

    opciones_contexto = []
    lineas = [f"📦 Productos de {categoria_nombre} (todas las agencias):"]
    for producto in productos_categoria:
        stock = await inventario_client.obtener_stock(producto["id"])
        cantidad = float(stock.get("cantidad_total", 0))
        precio = producto.get("precio_actual")
        precio_texto = f"Bs. {precio}" if precio is not None else "Precio no disponible"
        lineas.append(
            f"• {producto['nombre']} — 💰 {precio_texto} | 📊 Stock total: {int(cantidad)}"
        )
        opciones_contexto.append(
            {"id": producto["id"], "nombre": producto["nombre"], "categoria_id": categoria_id}
        )

    return ResultadoBot(
        respuesta="\n".join(lineas) + "\n\n✍️ Escribe el número o nombre del producto para ver el detalle.",
        opciones=[p["nombre"] for p in opciones_contexto],
        nuevo_estado="catalogo_general_productos",
        nuevo_contexto={
            "productos": opciones_contexto,
            "categoria_id": categoria_id,
            "categoria_nombre": categoria_nombre,
            "carrito": carrito,
        },
    )


async def handle_catalogo_general_productos(conversacion: ChatbotConversacion, texto: str) -> ResultadoBot:
    productos_contexto = conversacion.contexto.get("productos", [])
    carrito = conversacion.contexto.get("carrito")

    seleccion = resolver_seleccion(texto, productos_contexto)
    if not seleccion:
        return ResultadoBot(
            respuesta="❌ No reconocí ese producto. Escribe el número o nombre de la lista.",
            opciones=[p["nombre"] for p in productos_contexto],
            nuevo_estado="catalogo_general_productos",
            nuevo_contexto=conversacion.contexto,
        )

    producto = await catalogos_client.obtener_producto(seleccion["id"])
    stock = await inventario_client.obtener_stock(seleccion["id"])
    cantidad = float(stock.get("cantidad_total", 0))

    disponibilidad = "🟢 Disponible" if cantidad > 5 else f"⚠️ Últimas {int(cantidad)} unidades" if cantidad > 0 else "❌ Sin stock"
    precio = producto.get("precio_actual")
    precio_texto = f"Bs. {precio}" if precio is not None else "Precio no disponible"

    lineas = [
        f"📦 {producto['nombre']}",
        f"💰 Precio: {precio_texto}",
        f"📊 Stock total (todas las agencias): {disponibilidad}",
    ]
    if producto.get("descripcion"):
        lineas.append(f"📝 Descripción: {producto['descripcion']}")

    return ResultadoBot(
        respuesta="\n".join(lineas),
        opciones=["🔙 Menú principal"],
        nuevo_estado="menu",
        nuevo_contexto={"carrito": carrito} if carrito else {},
    )


STATE_HANDLERS = {
    "menu": handle_menu,
    "agencias": handle_agencias,
    "catalogo_categorias": handle_catalogo_categorias,
    "catalogo_productos": handle_catalogo_productos,
    "catalogo_general_categorias": handle_catalogo_general,
    "catalogo_general_productos": handle_catalogo_general_productos,
    "producto_detalle": handle_producto_detalle,
    "producto_cantidad": handle_producto_cantidad,
    "carrito": handle_carrito,
    "soporte": handle_soporte,
}

INTENT_HANDLERS = {
    "menu": handle_menu,
    "horario": handle_horario,
    "ubicacion": handle_ubicacion,
    "soporte": handle_soporte,
    "catalogo": handle_agencias,
    "catalogo_general": handle_catalogo_general,
    "carrito": handle_carrito,
}


ESTADOS_CON_LISTA_PENDIENTE = {
    "agencias": "agencias",
    "catalogo_categorias": "categorias",
    "catalogo_productos": "productos",
    "catalogo_general_categorias": "categorias",
    "catalogo_general_productos": "productos",
}

ESTADOS_SIN_SELECCION_PENDIENTE = {"menu", "soporte"}


def _es_opcion_de_estado_actual(conversacion: ChatbotConversacion, texto: str) -> bool:
    texto_normalizado = bot_config.normalizar(texto)
    if conversacion.estado == "producto_detalle":
        return any(
            p in texto_normalizado for p in ("ver mas", "mas productos", "menu", "agregar", "carrito")
        )
    if conversacion.estado in ("producto_cantidad", "carrito"):
        return True
    return False


def _hay_seleccion_pendiente_valida(conversacion: ChatbotConversacion, texto: str) -> bool:
    clave_contexto = ESTADOS_CON_LISTA_PENDIENTE.get(conversacion.estado)
    if not clave_contexto:
        return False
    opciones = conversacion.contexto.get(clave_contexto)
    if not opciones:
        return False
    return resolver_seleccion(texto, opciones) is not None


async def procesar_mensaje(db: AsyncSession, sesion_id: str, texto: str) -> ResultadoBot:
    conversacion = await conversacion_service.get_or_create(db, sesion_id)

    if _es_opcion_de_estado_actual(conversacion, texto) or _hay_seleccion_pendiente_valida(conversacion, texto):
        handler = STATE_HANDLERS[conversacion.estado]
    else:
        intent = await bot_config.detectar_intent(texto)
        if intent:
            handler = INTENT_HANDLERS[intent]
        elif conversacion.estado in ESTADOS_SIN_SELECCION_PENDIENTE:
            handler = handle_vendedor_ia
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
