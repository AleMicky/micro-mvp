from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.ventas import crud_factura
from app.schemas.ventas import FacturaCreate, FacturaResponse
from app.services.venta import venta_service

router = APIRouter(prefix="/facturas", tags=["facturas"])

@router.get("", response_model=list[FacturaResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await crud_factura.get_all(db, skip=skip, limit=limit)

@router.get("/{factura_id}", response_model=FacturaResponse)
async def obtener(factura_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_factura.get(db, factura_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return obj

@router.post("", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: FacturaCreate, db: AsyncSession = Depends(get_db)):
    return await venta_service.crear_factura(db, payload)
