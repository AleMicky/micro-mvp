from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.compras import crud_cotizacion
from app.schemas.compras import CotizacionCompraCreate, CotizacionCompraResponse, CotizacionCompraUpdate

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])


@router.get("", response_model=list[CotizacionCompraResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await crud_cotizacion.get_all(db, skip=skip, limit=limit)


@router.get("/{cotizacion_id}", response_model=CotizacionCompraResponse)
async def obtener(cotizacion_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_cotizacion.get(db, cotizacion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return obj


@router.post("", response_model=CotizacionCompraResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: CotizacionCompraCreate, db: AsyncSession = Depends(get_db)):
    return await crud_cotizacion.create(db, payload)


@router.put("/{cotizacion_id}", response_model=CotizacionCompraResponse)
async def actualizar(cotizacion_id: int, payload: CotizacionCompraUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud_cotizacion.get(db, cotizacion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return await crud_cotizacion.update(db, obj, payload)


@router.delete("/{cotizacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(cotizacion_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_cotizacion.get(db, cotizacion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    await crud_cotizacion.delete(db, obj)
