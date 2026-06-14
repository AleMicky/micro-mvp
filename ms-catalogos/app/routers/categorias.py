from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.categoria import crud_categoria
from app.schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaResponse])
async def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await crud_categoria.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)


@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def obtener_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    categoria = await crud_categoria.get(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return categoria


@router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def crear_categoria(payload: CategoriaCreate, db: AsyncSession = Depends(get_db)):
    return await crud_categoria.create(db, payload)


@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def actualizar_categoria(
    categoria_id: int,
    payload: CategoriaUpdate,
    db: AsyncSession = Depends(get_db),
):
    categoria = await crud_categoria.get(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return await crud_categoria.update(db, categoria, payload)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    categoria = await crud_categoria.get(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    await crud_categoria.delete(db, categoria)
