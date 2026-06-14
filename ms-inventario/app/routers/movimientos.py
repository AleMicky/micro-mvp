from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.movimiento import crud_movimiento
from app.schemas.movimiento import KardexResponse, MovimientoInventarioResponse

router = APIRouter(tags=["movimientos"])


@router.get("/movimientos", response_model=list[MovimientoInventarioResponse])
async def listar_movimientos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud_movimiento.get_all(db, skip=skip, limit=limit)


@router.get("/movimientos/producto/{producto_id}", response_model=list[MovimientoInventarioResponse])
async def listar_movimientos_por_producto(
    producto_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud_movimiento.get_all(
        db, skip=skip, limit=limit, producto_id=producto_id
    )


@router.get("/movimientos/almacen/{almacen_id}", response_model=list[MovimientoInventarioResponse])
async def listar_movimientos_por_almacen(
    almacen_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud_movimiento.get_all(
        db, skip=skip, limit=limit, almacen_id=almacen_id
    )


@router.get("/kardex/producto/{producto_id}", response_model=KardexResponse)
async def obtener_kardex_producto(
    producto_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    movimientos = await crud_movimiento.get_kardex(
        db, producto_id=producto_id, skip=skip, limit=limit
    )
    return KardexResponse(
        producto_id=producto_id,
        total_movimientos=len(movimientos),
        movimientos=movimientos,
    )
