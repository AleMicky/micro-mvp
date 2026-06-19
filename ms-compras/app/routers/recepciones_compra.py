from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.compras import (
    RecepcionCompraCreate,
    RecepcionCompraResponse,
    RecepcionCompraUpdate,
)
from app.services.recepcion_compra_service import recepcion_compra_service

router = APIRouter(prefix="/recepciones-compra", tags=["recepciones-compra"])


@router.get("", response_model=list[RecepcionCompraResponse])
async def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await recepcion_compra_service.listar(db, skip=skip, limit=limit)


@router.get("/{recepcion_id}", response_model=RecepcionCompraResponse)
async def obtener(recepcion_id: int, db: AsyncSession = Depends(get_db)):
    return await recepcion_compra_service.obtener(db, recepcion_id)


@router.post("", response_model=RecepcionCompraResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: RecepcionCompraCreate, db: AsyncSession = Depends(get_db)):
    return await recepcion_compra_service.crear(db, payload)


@router.put("/{recepcion_id}", response_model=RecepcionCompraResponse)
async def actualizar(recepcion_id: int, payload: RecepcionCompraUpdate, db: AsyncSession = Depends(get_db)):
    return await recepcion_compra_service.actualizar(db, recepcion_id, payload)


@router.delete("/{recepcion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(recepcion_id: int, db: AsyncSession = Depends(get_db)):
    await recepcion_compra_service.eliminar(db, recepcion_id)


@router.post("/{recepcion_id}/confirmar", response_model=RecepcionCompraResponse)
async def confirmar(recepcion_id: int, db: AsyncSession = Depends(get_db)):
    return await recepcion_compra_service.confirmar(db, recepcion_id)


@router.post("/{recepcion_id}/cancelar", response_model=RecepcionCompraResponse)
async def cancelar(recepcion_id: int, db: AsyncSession = Depends(get_db)):
    return await recepcion_compra_service.cancelar(db, recepcion_id)
