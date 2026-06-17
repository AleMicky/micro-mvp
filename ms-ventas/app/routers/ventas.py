from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.ventas import crud_venta
from app.schemas.ventas import VentaCreate, VentaResponse, VentaUpdate
from app.services.venta import venta_service

router = APIRouter(prefix="/ventas", tags=["ventas"])

@router.get("", response_model=list[VentaResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await crud_venta.get_all(db, skip=skip, limit=limit)

@router.get("/{venta_id}", response_model=VentaResponse)
async def obtener(venta_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_venta.get(db, venta_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return obj

@router.post("", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: VentaCreate, db: AsyncSession = Depends(get_db)):
    return await crud_venta.create(db, payload)

@router.put("/{venta_id}", response_model=VentaResponse)
async def actualizar(venta_id: int, payload: VentaUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud_venta.get(db, venta_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return await crud_venta.update(db, obj, payload)

@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(venta_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_venta.get(db, venta_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    await crud_venta.delete(db, obj)

@router.post("/{venta_id}/confirmar", response_model=VentaResponse)
async def confirmar(venta_id: int, db: AsyncSession = Depends(get_db)):
    return await venta_service.confirmar_venta(db, venta_id)
