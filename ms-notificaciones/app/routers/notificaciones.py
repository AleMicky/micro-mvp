from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.notificacion import Notificacion
from app.schemas.notificacion import NotificacionResponse

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.get("", response_model=list[NotificacionResponse])
async def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Notificacion).offset(skip).limit(limit).order_by(Notificacion.id.desc())
    return list((await db.execute(stmt)).scalars().all())


@router.get("/cliente/{cliente_id}", response_model=list[NotificacionResponse])
async def listar_por_cliente(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Notificacion)
        .where(Notificacion.cliente_id == cliente_id)
        .offset(skip)
        .limit(limit)
        .order_by(Notificacion.id.desc())
    )
    items = list((await db.execute(stmt)).scalars().all())
    return items
