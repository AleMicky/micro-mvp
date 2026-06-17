from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.finanzas import (
    BancoCreate,
    BancoResponse,
    BancoUpdate,
    CajaCreate,
    CajaResponse,
    CajaUpdate,
    CobroCreate,
    CobroResponse,
    CuentaPorCobrarCreate,
    CuentaPorCobrarResponse,
    CuentaPorPagarCreate,
    CuentaPorPagarResponse,
    MovimientoBancarioResponse,
    MovimientoCajaResponse,
    PagoCreate,
    PagoResponse,
)
from app.services.finanzas import finanzas_service

router = APIRouter(tags=["finanzas"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ms-finanzas"}


@router.get("/cuentas-por-cobrar", response_model=list[CuentaPorCobrarResponse])
async def listar_cxc(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await finanzas_service.listar_cxc(db, skip, limit)


@router.post("/cuentas-por-cobrar", response_model=CuentaPorCobrarResponse, status_code=status.HTTP_201_CREATED)
async def crear_cxc(payload: CuentaPorCobrarCreate, db: AsyncSession = Depends(get_db)):
    return await finanzas_service.crear_cxc(db, payload)


@router.get("/cuentas-por-pagar", response_model=list[CuentaPorPagarResponse])
async def listar_cxp(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await finanzas_service.listar_cxp(db, skip, limit)


@router.post("/cuentas-por-pagar", response_model=CuentaPorPagarResponse, status_code=status.HTTP_201_CREATED)
async def crear_cxp(payload: CuentaPorPagarCreate, db: AsyncSession = Depends(get_db)):
    return await finanzas_service.crear_cxp(db, payload)


@router.post("/cobros", response_model=CobroResponse, status_code=status.HTTP_201_CREATED)
async def registrar_cobro(payload: CobroCreate, db: AsyncSession = Depends(get_db)):
    return await finanzas_service.registrar_cobro(db, payload)


@router.post("/pagos", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_pago(payload: PagoCreate, db: AsyncSession = Depends(get_db)):
    return await finanzas_service.registrar_pago(db, payload)


@router.get("/cajas", response_model=list[CajaResponse])
async def listar_cajas(db: AsyncSession = Depends(get_db)):
    return await finanzas_service.listar_cajas(db)


@router.post("/cajas", response_model=CajaResponse, status_code=status.HTTP_201_CREATED)
async def crear_caja(payload: CajaCreate, db: AsyncSession = Depends(get_db)):
    return await finanzas_service.crear_caja(db, payload)


@router.put("/cajas/{caja_id}", response_model=CajaResponse)
async def actualizar_caja(caja_id: int, payload: CajaUpdate, db: AsyncSession = Depends(get_db)):
    return await finanzas_service.actualizar_caja(db, caja_id, payload)


@router.delete("/cajas/{caja_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_caja(caja_id: int, db: AsyncSession = Depends(get_db)):
    await finanzas_service.eliminar_caja(db, caja_id)


@router.get("/bancos", response_model=list[BancoResponse])
async def listar_bancos(db: AsyncSession = Depends(get_db)):
    return await finanzas_service.listar_bancos(db)


@router.post("/bancos", response_model=BancoResponse, status_code=status.HTTP_201_CREATED)
async def crear_banco(payload: BancoCreate, db: AsyncSession = Depends(get_db)):
    return await finanzas_service.crear_banco(db, payload)


@router.put("/bancos/{banco_id}", response_model=BancoResponse)
async def actualizar_banco(banco_id: int, payload: BancoUpdate, db: AsyncSession = Depends(get_db)):
    return await finanzas_service.actualizar_banco(db, banco_id, payload)


@router.delete("/bancos/{banco_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_banco(banco_id: int, db: AsyncSession = Depends(get_db)):
    await finanzas_service.eliminar_banco(db, banco_id)


@router.get("/movimientos-caja", response_model=list[MovimientoCajaResponse])
async def movimientos_caja(db: AsyncSession = Depends(get_db)):
    return await finanzas_service.movimientos_caja(db)


@router.get("/movimientos-bancarios", response_model=list[MovimientoBancarioResponse])
async def movimientos_bancarios(db: AsyncSession = Depends(get_db)):
    return await finanzas_service.movimientos_bancarios(db)


@router.get("/cobros", response_model=list[CobroResponse])
async def listar_cobros(db: AsyncSession = Depends(get_db)):
    return await finanzas_service.listar_cobros(db)


@router.get("/pagos", response_model=list[PagoResponse])
async def listar_pagos(db: AsyncSession = Depends(get_db)):
    return await finanzas_service.listar_pagos(db)
