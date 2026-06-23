from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.ventas import crud_cotizacion
from app.schemas.ventas import CotizacionVentaCreate, CotizacionVentaResponse, CotizacionVentaUpdate, VentaResponse
from app.services.venta import venta_service

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])

@router.get("", response_model=list[CotizacionVentaResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await crud_cotizacion.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=CotizacionVentaResponse)
async def obtener(id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_cotizacion.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return obj

@router.post("", response_model=CotizacionVentaResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: CotizacionVentaCreate, db: AsyncSession = Depends(get_db)):
    return await crud_cotizacion.create(db, payload)

@router.put("/{id}", response_model=CotizacionVentaResponse)
async def actualizar(id: int, payload: CotizacionVentaUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud_cotizacion.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return await crud_cotizacion.update(db, obj, payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_cotizacion.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    await crud_cotizacion.delete(db, obj)

@router.post("/{id}/aprobar", response_model=VentaResponse)
async def aprobar(id: int, db: AsyncSession = Depends(get_db)):
    return await venta_service.aprobar_cotizacion(db, id)
