import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.conversacion import (
    ConversacionListItem,
    ConversacionResponse,
    MensajeItem,
    MensajeRequest,
    MensajeResponse,
    ResponderRequest,
    TunnelUrlResponse,
)
from app.services import bot, bot_config
from app.services.conversacion import conversacion_service
from app.services.conversacion_etiqueta import conversacion_etiqueta_service
from app.services.etiqueta import etiqueta_service
from app.services.mensaje import mensaje_service
from app.services.respuesta_agente import respuesta_agente_service

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

TUNNEL_URL_PATTERN = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")


@router.get("/tunnel-url", response_model=TunnelUrlResponse)
async def obtener_tunnel_url():
    if not settings.tunnel_log_path:
        return TunnelUrlResponse(url=None, activo=False)
    log_path = Path(settings.tunnel_log_path)
    if not log_path.exists():
        return TunnelUrlResponse(url=None, activo=False)
    raw = log_path.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8"
    contenido = raw.decode(encoding, errors="ignore")
    coincidencias = TUNNEL_URL_PATTERN.findall(contenido)
    if not coincidencias:
        return TunnelUrlResponse(url=None, activo=False)
    return TunnelUrlResponse(url=coincidencias[-1], activo=True)


@router.post("/mensaje", response_model=MensajeResponse)
async def enviar_mensaje(payload: MensajeRequest, db: AsyncSession = Depends(get_db)):
    try:
        resultado = await bot.procesar_mensaje(db, payload.sesion_id, payload.texto)
    except HTTPException:
        return MensajeResponse(
            respuesta=bot_config.MENSAJE_ERROR_SERVICIO,
            opciones=["Menú principal"],
            estado="menu",
        )
    return MensajeResponse(
        respuesta=resultado.respuesta,
        opciones=resultado.opciones,
        estado=resultado.nuevo_estado,
    )


@router.get("/conversaciones", response_model=list[ConversacionListItem])
async def listar_conversaciones(canal: str | None = "whatsapp", db: AsyncSession = Depends(get_db)):
    conversaciones = await conversacion_service.listar(db, canal=canal)
    etiquetas_por_conversacion = await conversacion_etiqueta_service.listar_por_conversaciones(
        db, [c.id for c in conversaciones]
    )
    items = []
    for conversacion in conversaciones:
        ultimo = await mensaje_service.ultimo_por_conversacion(db, conversacion.id)
        items.append(
            ConversacionListItem(
                id=conversacion.id,
                sesion_id=conversacion.sesion_id,
                canal=conversacion.canal,
                estado=conversacion.estado,
                actualizado_en=conversacion.actualizado_en,
                ultimo_mensaje=ultimo.texto if ultimo else None,
                ultimo_mensaje_en=ultimo.creado_en if ultimo else None,
                ultima_direccion=ultimo.direccion if ultimo else None,
                etiquetas=etiquetas_por_conversacion.get(conversacion.id, []),
            )
        )
    return items


@router.get("/conversaciones/{conversacion_id}/mensajes", response_model=list[MensajeItem])
async def obtener_mensajes(conversacion_id: int, db: AsyncSession = Depends(get_db)):
    conversacion = await conversacion_service.get_by_id(db, conversacion_id)
    if not conversacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    return await mensaje_service.listar_por_conversacion(db, conversacion_id)


@router.post(
    "/conversaciones/{conversacion_id}/responder",
    response_model=MensajeItem,
    status_code=status.HTTP_201_CREATED,
)
async def responder_conversacion(
    conversacion_id: int, payload: ResponderRequest, db: AsyncSession = Depends(get_db)
):
    return await respuesta_agente_service.responder(db, conversacion_id, payload.texto)


@router.post(
    "/conversaciones/{conversacion_id}/responder-adjunto",
    response_model=MensajeItem,
    status_code=status.HTTP_201_CREATED,
)
async def responder_conversacion_con_adjunto(
    conversacion_id: int,
    archivo: UploadFile = File(...),
    caption: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    contenido = await archivo.read()
    return await respuesta_agente_service.responder_con_adjunto(
        db,
        conversacion_id,
        contenido,
        archivo.content_type or "application/octet-stream",
        archivo.filename or "archivo",
        caption,
    )


@router.post("/conversaciones/{conversacion_id}/etiquetas/{etiqueta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def asignar_etiqueta_conversacion(conversacion_id: int, etiqueta_id: int, db: AsyncSession = Depends(get_db)):
    conversacion = await conversacion_service.get_by_id(db, conversacion_id)
    if not conversacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    etiqueta = await etiqueta_service.get_by_id(db, etiqueta_id)
    if not etiqueta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta no encontrada")
    await conversacion_etiqueta_service.asignar(db, conversacion_id, etiqueta_id)


@router.delete("/conversaciones/{conversacion_id}/etiquetas/{etiqueta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desasignar_etiqueta_conversacion(conversacion_id: int, etiqueta_id: int, db: AsyncSession = Depends(get_db)):
    await conversacion_etiqueta_service.desasignar(db, conversacion_id, etiqueta_id)


@router.get("/conversaciones/{sesion_id}", response_model=ConversacionResponse)
async def obtener_conversacion(sesion_id: str, db: AsyncSession = Depends(get_db)):
    conversacion = await conversacion_service.get_by_sesion(db, sesion_id)
    if not conversacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    etiquetas = await conversacion_etiqueta_service.listar_por_conversacion(db, conversacion.id)
    return ConversacionResponse(
        id=conversacion.id,
        sesion_id=conversacion.sesion_id,
        canal=conversacion.canal,
        estado=conversacion.estado,
        contexto=conversacion.contexto,
        cliente_id=conversacion.cliente_id,
        creado_en=conversacion.creado_en,
        actualizado_en=conversacion.actualizado_en,
        etiquetas=etiquetas,
    )
