from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.compras import RecepcionCompraResponse
from app.services.recepcion_compra_service import recepcion_compra_service

router = APIRouter(prefix="/recepciones", tags=["recepciones"])


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
