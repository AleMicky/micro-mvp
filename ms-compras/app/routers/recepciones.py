from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.compras import crud_recepcion
from app.schemas.compras import RecepcionCompraCreate, RecepcionCompraResponse
from app.services.compra import compra_service

router = APIRouter(prefix="/recepciones", tags=["recepciones"])


@router.get("", response_model=list[RecepcionCompraResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await crud_recepcion.get_all(db, skip=skip, limit=limit)


@router.get("/{recepcion_id}", response_model=RecepcionCompraResponse)
async def obtener(recepcion_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_recepcion.get(db, recepcion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Recepción no encontrada")
    return obj


@router.post("", response_model=RecepcionCompraResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: RecepcionCompraCreate, db: AsyncSession = Depends(get_db)):
    return await compra_service.registrar_recepcion(db, payload)
