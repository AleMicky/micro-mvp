from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.compras import OrdenCompraResponse
from app.services.orden_compra_service import orden_compra_service

router = APIRouter(prefix="/ordenes", tags=["ordenes"])


@router.get("", response_model=list[OrdenCompraResponse])
async def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await orden_compra_service.listar(db, skip=skip, limit=limit)


@router.get("/{orden_id}", response_model=OrdenCompraResponse)
async def obtener(orden_id: int, db: AsyncSession = Depends(get_db)):
    return await orden_compra_service.obtener(db, orden_id)
