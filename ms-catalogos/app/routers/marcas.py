from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.marca import crud_marca
from app.schemas.marca import MarcaCreate, MarcaResponse, MarcaUpdate

router = APIRouter(prefix="/marcas", tags=["marcas"])


@router.get("", response_model=list[MarcaResponse])
async def listar_marcas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await crud_marca.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)


@router.get("/{marca_id}", response_model=MarcaResponse)
async def obtener_marca(marca_id: int, db: AsyncSession = Depends(get_db)):
    marca = await crud_marca.get(db, marca_id)
    if not marca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
    return marca


@router.post("", response_model=MarcaResponse, status_code=status.HTTP_201_CREATED)
async def crear_marca(payload: MarcaCreate, db: AsyncSession = Depends(get_db)):
    return await crud_marca.create(db, payload)


@router.put("/{marca_id}", response_model=MarcaResponse)
async def actualizar_marca(
    marca_id: int,
    payload: MarcaUpdate,
    db: AsyncSession = Depends(get_db),
):
    marca = await crud_marca.get(db, marca_id)
    if not marca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
    return await crud_marca.update(db, marca, payload)


@router.delete("/{marca_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_marca(marca_id: int, db: AsyncSession = Depends(get_db)):
    marca = await crud_marca.get(db, marca_id)
    if not marca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
    await crud_marca.delete(db, marca)
