from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.existencia import crud_existencia
from app.models.almacen import Almacen
from app.schemas.existencia import ExistenciaResponse
from app.schemas.operacion import (
    AjusteInventarioResponse,
    StockOperacionResponse,
    TransferenciaInventarioResponse,
)
from app.schemas.stock import (
    StockAjusteRequest,
    StockIngresoRequest,
    StockSalidaRequest,
    StockTransferenciaRequest,
)
from app.services.excel import saldo_consolidado
from app.services.stock import stock_service

router = APIRouter(prefix="/stock", tags=["stock"])


@router.post("/ingreso", response_model=StockOperacionResponse, status_code=status.HTTP_201_CREATED)
async def registrar_ingreso(payload: StockIngresoRequest, db: AsyncSession = Depends(get_db)):
    return await stock_service.ingreso(db, payload)


@router.post("/salida", response_model=StockOperacionResponse, status_code=status.HTTP_201_CREATED)
async def registrar_salida(payload: StockSalidaRequest, db: AsyncSession = Depends(get_db)):
    return await stock_service.salida(db, payload)


@router.post("/ajuste", response_model=AjusteInventarioResponse, status_code=status.HTTP_201_CREATED)
async def registrar_ajuste(payload: StockAjusteRequest, db: AsyncSession = Depends(get_db)):
    return await stock_service.ajuste(db, payload)


@router.post(
    "/transferencia",
    response_model=TransferenciaInventarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_transferencia(
    payload: StockTransferenciaRequest,
    db: AsyncSession = Depends(get_db),
):
    return await stock_service.transferencia(db, payload)


@router.get("/sucursal/{sucursal_id}", response_model=list[ExistenciaResponse])
async def stock_por_sucursal(sucursal_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Almacen.id).where(Almacen.sucursal_id == sucursal_id)
    almacen_ids = list((await db.execute(stmt)).scalars().all())
    if not almacen_ids:
        stmt_nombre = select(Almacen.id).where(Almacen.nombre.ilike(f"%{sucursal_id}%"))
        almacen_ids = list((await db.execute(stmt_nombre)).scalars().all())
    if not almacen_ids:
        raise HTTPException(status_code=404, detail="Sin almacenes para la sucursal")
    items: list = []
    for aid in almacen_ids:
        items.extend(await crud_existencia.get_all(db, almacen_id=aid, limit=500))
    return items


@router.get("/consolidado/producto/{producto_id}")
async def consolidado_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    return await saldo_consolidado(db, producto_id)
