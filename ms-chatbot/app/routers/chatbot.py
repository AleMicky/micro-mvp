from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.conversacion import (
    ConversacionListItem,
    ConversacionResponse,
    MensajeItem,
    MensajeRequest,
    MensajeResponse,
)
from app.services import bot, bot_config
from app.services.conversacion import conversacion_service
from app.services.mensaje import mensaje_service

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


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
            )
        )
    return items


@router.get("/conversaciones/{conversacion_id}/mensajes", response_model=list[MensajeItem])
async def obtener_mensajes(conversacion_id: int, db: AsyncSession = Depends(get_db)):
    conversacion = await conversacion_service.get_by_id(db, conversacion_id)
    if not conversacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    return await mensaje_service.listar_por_conversacion(db, conversacion_id)


@router.get("/conversaciones/{sesion_id}", response_model=ConversacionResponse)
async def obtener_conversacion(sesion_id: str, db: AsyncSession = Depends(get_db)):
    conversacion = await conversacion_service.get_by_sesion(db, sesion_id)
    if not conversacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    return conversacion
