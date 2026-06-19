from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.compras import ProveedorCreate, ProveedorResponse, ProveedorUpdate
from app.services.proveedor_service import proveedor_service

router = APIRouter(prefix="/proveedores", tags=["proveedores"])


@router.get("", response_model=list[ProveedorResponse])
async def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await proveedor_service.listar(db, skip=skip, limit=limit, solo_activos=solo_activos)


@router.get("/{proveedor_id}", response_model=ProveedorResponse)
async def obtener(proveedor_id: int, db: AsyncSession = Depends(get_db)):
    return await proveedor_service.obtener(db, proveedor_id)


@router.post("", response_model=ProveedorResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: ProveedorCreate, db: AsyncSession = Depends(get_db)):
    return await proveedor_service.crear(db, payload)


@router.put("/{proveedor_id}", response_model=ProveedorResponse)
async def actualizar(proveedor_id: int, payload: ProveedorUpdate, db: AsyncSession = Depends(get_db)):
    return await proveedor_service.actualizar(db, proveedor_id, payload)


@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(proveedor_id: int, db: AsyncSession = Depends(get_db)):
    await proveedor_service.eliminar(db, proveedor_id)
