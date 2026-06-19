from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.company import crud_sucursal
from app.schemas.company import SucursalCreate, SucursalResponse, SucursalUpdate

router = APIRouter(prefix="/sucursales", tags=["sucursales"])


@router.get("", response_model=list[SucursalResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await crud_sucursal.get_all(db, skip=skip, limit=limit)


@router.get("/{sucursal_id}", response_model=SucursalResponse)
async def obtener(sucursal_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_sucursal.get(db, sucursal_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sucursal no encontrada")
    return obj


@router.post("", response_model=SucursalResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: SucursalCreate, db: AsyncSession = Depends(get_db)):
    return await crud_sucursal.create(db, payload)


@router.put("/{sucursal_id}", response_model=SucursalResponse)
async def actualizar(sucursal_id: int, payload: SucursalUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud_sucursal.get(db, sucursal_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sucursal no encontrada")
    return await crud_sucursal.update(db, obj, payload)


@router.delete("/{sucursal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(sucursal_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_sucursal.get(db, sucursal_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sucursal no encontrada")
    await crud_sucursal.delete(db, obj)
