from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.compras import crud_proveedor
from app.schemas.compras import ProveedorCreate, ProveedorResponse, ProveedorUpdate

router = APIRouter(prefix="/proveedores", tags=["proveedores"])


@router.get("", response_model=list[ProveedorResponse])
async def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await crud_proveedor.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)


@router.get("/{proveedor_id}", response_model=ProveedorResponse)
async def obtener(proveedor_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_proveedor.get(db, proveedor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return obj


@router.post("", response_model=ProveedorResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: ProveedorCreate, db: AsyncSession = Depends(get_db)):
    obj = await crud_proveedor.create(db, payload)
    await db.commit()
    return obj


@router.put("/{proveedor_id}", response_model=ProveedorResponse)
async def actualizar(proveedor_id: int, payload: ProveedorUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud_proveedor.get(db, proveedor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    obj = await crud_proveedor.update(db, obj, payload)
    await db.commit()
    return obj


@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(proveedor_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_proveedor.get(db, proveedor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    await crud_proveedor.delete(db, obj)
    await db.commit()
