from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
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
