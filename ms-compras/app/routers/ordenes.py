from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.compras import crud_orden
from app.schemas.compras import OrdenCompraCreate, OrdenCompraResponse, OrdenCompraUpdate
from app.services.compra import compra_service

router = APIRouter(prefix="/ordenes", tags=["ordenes"])


@router.get("", response_model=list[OrdenCompraResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await crud_orden.get_all(db, skip=skip, limit=limit)


@router.get("/{orden_id}", response_model=OrdenCompraResponse)
async def obtener(orden_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_orden.get(db, orden_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return obj


@router.post("", response_model=OrdenCompraResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: OrdenCompraCreate, db: AsyncSession = Depends(get_db)):
    return await crud_orden.create(db, payload)


@router.put("/{orden_id}", response_model=OrdenCompraResponse)
async def actualizar(orden_id: int, payload: OrdenCompraUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud_orden.get(db, orden_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return await crud_orden.update(db, obj, payload)


@router.delete("/{orden_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(orden_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_orden.get(db, orden_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    await crud_orden.delete(db, obj)


@router.post("/{orden_id}/aprobar", response_model=OrdenCompraResponse)
async def aprobar(orden_id: int, db: AsyncSession = Depends(get_db)):
    return await compra_service.aprobar_orden(db, orden_id)
