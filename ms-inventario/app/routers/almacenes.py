from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.almacen import crud_almacen
from app.schemas.almacen import AlmacenCreate, AlmacenResponse, AlmacenUpdate
from app.services.almacen import almacen_service, almacen_to_response

router = APIRouter(prefix="/almacenes", tags=["almacenes"])


@router.get("", response_model=list[AlmacenResponse])
async def listar_almacenes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
):
    almacenes = await crud_almacen.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)
    return [almacen_to_response(a) for a in almacenes]


@router.get("/{almacen_id}", response_model=AlmacenResponse)
async def obtener_almacen(almacen_id: int, db: AsyncSession = Depends(get_db)):
    almacen = await crud_almacen.get(db, almacen_id)
    if not almacen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Almacén no encontrado")
    return almacen_to_response(almacen)


@router.post("", response_model=AlmacenResponse, status_code=status.HTTP_201_CREATED)
async def crear_almacen(payload: AlmacenCreate, db: AsyncSession = Depends(get_db)):
    return await almacen_service.crear(db, payload)


@router.put("/{almacen_id}", response_model=AlmacenResponse)
async def actualizar_almacen(
    almacen_id: int,
    payload: AlmacenUpdate,
    db: AsyncSession = Depends(get_db),
):
    almacen = await crud_almacen.get(db, almacen_id)
    if not almacen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Almacén no encontrado")
    return await almacen_service.actualizar(db, almacen, payload)


@router.delete("/{almacen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_almacen(almacen_id: int, db: AsyncSession = Depends(get_db)):
    almacen = await crud_almacen.get(db, almacen_id)
    if not almacen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Almacén no encontrado")
    await crud_almacen.delete(db, almacen)
