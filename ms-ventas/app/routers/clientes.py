from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.ventas import crud_cliente
from app.schemas.ventas import ClienteCreate, ClienteResponse, ClienteUpdate

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.get("", response_model=list[ClienteResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), solo_activos: bool = False, db: AsyncSession = Depends(get_db)):
    return await crud_cliente.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)

@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obtener(cliente_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_cliente.get(db, cliente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return obj

@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: ClienteCreate, db: AsyncSession = Depends(get_db)):
    obj = await crud_cliente.create(db, payload)
    await db.commit()
    return obj

@router.put("/{cliente_id}", response_model=ClienteResponse)
async def actualizar(cliente_id: int, payload: ClienteUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud_cliente.get(db, cliente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    obj = await crud_cliente.update(db, obj, payload)
    await db.commit()
    return obj

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(cliente_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud_cliente.get(db, cliente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    await crud_cliente.delete(db, obj)
    await db.commit()
