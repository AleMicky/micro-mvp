from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.producto import crud_producto
from app.events.publisher import publish_event
from app.schemas.producto import ProductoCreate, ProductoResponse, ProductoUpdate

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("", response_model=list[ProductoResponse])
async def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await crud_producto.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)


@router.get("/codigo/{codigo}", response_model=ProductoResponse)
async def obtener_producto_por_codigo(codigo: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.producto import Producto

    stmt = select(Producto).where(Producto.codigo == codigo)
    producto = (await db.execute(stmt)).scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


@router.get("/{producto_id}", response_model=ProductoResponse)
async def obtener_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await crud_producto.get(db, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def crear_producto(payload: ProductoCreate, db: AsyncSession = Depends(get_db)):
    producto = await crud_producto.create(db, payload)
    await publish_event("ProductCreated", {"producto_id": producto.id, "codigo": producto.codigo, "nombre": producto.nombre})
    return producto


@router.put("/{producto_id}", response_model=ProductoResponse)
async def actualizar_producto(
    producto_id: int,
    payload: ProductoUpdate,
    db: AsyncSession = Depends(get_db),
):
    producto = await crud_producto.get(db, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    updated = await crud_producto.update(db, producto, payload)
    await publish_event("ProductUpdated", {"producto_id": updated.id, "codigo": updated.codigo})
    return updated


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await crud_producto.get(db, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    producto_id_val = producto.id
    codigo = producto.codigo
    await crud_producto.delete(db, producto)
    await publish_event("ProductDeleted", {"producto_id": producto_id_val, "codigo": codigo})
