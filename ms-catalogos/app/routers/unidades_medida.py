from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.unidad_medida import crud_unidad_medida
from app.schemas.unidad_medida import (
    UnidadMedidaCreate,
    UnidadMedidaResponse,
    UnidadMedidaUpdate,
)

router = APIRouter(prefix="/unidades-medida", tags=["unidades-medida"])


@router.get("", response_model=list[UnidadMedidaResponse])
async def listar_unidades_medida(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await crud_unidad_medida.get_all(
        db, skip=skip, limit=limit, solo_activos=solo_activos
    )


@router.get("/{unidad_id}", response_model=UnidadMedidaResponse)
async def obtener_unidad_medida(unidad_id: int, db: AsyncSession = Depends(get_db)):
    unidad = await crud_unidad_medida.get(db, unidad_id)
    if not unidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidad de medida no encontrada"
        )
    return unidad


@router.post("", response_model=UnidadMedidaResponse, status_code=status.HTTP_201_CREATED)
async def crear_unidad_medida(payload: UnidadMedidaCreate, db: AsyncSession = Depends(get_db)):
    return await crud_unidad_medida.create(db, payload)


@router.put("/{unidad_id}", response_model=UnidadMedidaResponse)
async def actualizar_unidad_medida(
    unidad_id: int,
    payload: UnidadMedidaUpdate,
    db: AsyncSession = Depends(get_db),
):
    unidad = await crud_unidad_medida.get(db, unidad_id)
    if not unidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidad de medida no encontrada"
        )
    return await crud_unidad_medida.update(db, unidad, payload)


@router.delete("/{unidad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_unidad_medida(unidad_id: int, db: AsyncSession = Depends(get_db)):
    unidad = await crud_unidad_medida.get(db, unidad_id)
    if not unidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unidad de medida no encontrada"
        )
    await crud_unidad_medida.delete(db, unidad)
