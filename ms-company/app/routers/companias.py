from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.company import crud_compania
from app.schemas.company import CompaniaCreate, CompaniaResponse, CompaniaUpdate

router = APIRouter(prefix="/companias", tags=["companias"])


@router.get("", response_model=list[CompaniaResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await crud_compania.get_all(db, skip=skip, limit=limit)


@router.get("/{compania_id}", response_model=CompaniaResponse)
async def obtener(compania_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_compania.get(db, compania_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañía no encontrada")
    return obj


@router.post("", response_model=CompaniaResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: CompaniaCreate, db: AsyncSession = Depends(get_db)):
    return await crud_compania.create(db, payload)


@router.put("/{compania_id}", response_model=CompaniaResponse)
async def actualizar(compania_id: int, payload: CompaniaUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud_compania.get(db, compania_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañía no encontrada")
    return await crud_compania.update(db, obj, payload)


@router.delete("/{compania_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(compania_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_compania.get(db, compania_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañía no encontrada")
    await crud_compania.delete(db, obj)


@router.get("/{compania_id}/sucursales", response_model=list)
async def listar_sucursales_compania(compania_id: int, db: AsyncSession = Depends(get_db)):
    from app.crud.company import crud_sucursal
    from app.schemas.company import SucursalResponse

    compania = await crud_compania.get(db, compania_id)
    if not compania:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañía no encontrada")
    sucursales = await crud_sucursal.get_by_compania(db, compania_id)
    return [SucursalResponse.model_validate(s) for s in sucursales]
