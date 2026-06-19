from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.compras import OrdenCompraCreate, OrdenCompraResponse, OrdenCompraUpdate
from app.services.orden_compra_service import orden_compra_service

router = APIRouter(prefix="/ordenes-compra", tags=["ordenes-compra"])


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


@router.post("", response_model=OrdenCompraResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: OrdenCompraCreate, db: AsyncSession = Depends(get_db)):
    return await orden_compra_service.crear(db, payload)


@router.put("/{orden_id}", response_model=OrdenCompraResponse)
async def actualizar(orden_id: int, payload: OrdenCompraUpdate, db: AsyncSession = Depends(get_db)):
    return await orden_compra_service.actualizar(db, orden_id, payload)


@router.delete("/{orden_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(orden_id: int, db: AsyncSession = Depends(get_db)):
    await orden_compra_service.eliminar(db, orden_id)


@router.post("/{orden_id}/aprobar", response_model=OrdenCompraResponse)
async def aprobar(orden_id: int, db: AsyncSession = Depends(get_db)):
    return await orden_compra_service.aprobar(db, orden_id)


@router.post("/{orden_id}/cancelar", response_model=OrdenCompraResponse)
async def cancelar(orden_id: int, db: AsyncSession = Depends(get_db)):
    return await orden_compra_service.cancelar(db, orden_id)
