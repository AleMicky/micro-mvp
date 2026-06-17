from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Caja,
    Cobro,
    CuentaBancaria,
    CuentaPorCobrar,
    CuentaPorPagar,
    MovimientoBancario,
    MovimientoCaja,
    Pago,
)
from app.schemas.finanzas import (
    BancoCreate,
    BancoUpdate,
    CajaCreate,
    CajaUpdate,
    CobroCreate,
    CuentaPorCobrarCreate,
    CuentaPorPagarCreate,
    PagoCreate,
)
from app.models import Banco


async def _next_codigo(db: AsyncSession, prefix: str, model) -> str:
    result = await db.execute(select(model.id).order_by(model.id.desc()).limit(1))
    last_id = result.scalar_one_or_none() or 0
    return f"{prefix}-{last_id + 1:05d}"


class FinanzasService:
    async def listar_cxc(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        stmt = select(CuentaPorCobrar).offset(skip).limit(limit).order_by(CuentaPorCobrar.id.desc())
        return list((await db.execute(stmt)).scalars().all())

    async def listar_cxp(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        stmt = select(CuentaPorPagar).offset(skip).limit(limit).order_by(CuentaPorPagar.id.desc())
        return list((await db.execute(stmt)).scalars().all())

    async def crear_cxc(self, db: AsyncSession, payload: CuentaPorCobrarCreate) -> CuentaPorCobrar:
        codigo = await _next_codigo(db, "CXC", CuentaPorCobrar)
        cuenta = CuentaPorCobrar(
            codigo=codigo,
            referencia_tipo=payload.referencia_tipo,
            referencia_id=payload.referencia_id,
            tercero_id=payload.tercero_id,
            tercero_tipo=payload.tercero_tipo,
            monto=payload.monto,
            saldo=payload.monto,
            estado="PENDIENTE",
            fecha_vencimiento=payload.fecha_vencimiento,
            descripcion=payload.descripcion,
        )
        db.add(cuenta)
        await db.commit()
        await db.refresh(cuenta)
        return cuenta

    async def crear_cxp(self, db: AsyncSession, payload: CuentaPorPagarCreate) -> CuentaPorPagar:
        codigo = await _next_codigo(db, "CXP", CuentaPorPagar)
        cuenta = CuentaPorPagar(
            codigo=codigo,
            referencia_tipo=payload.referencia_tipo,
            referencia_id=payload.referencia_id,
            tercero_id=payload.tercero_id,
            tercero_tipo=payload.tercero_tipo,
            monto=payload.monto,
            saldo=payload.monto,
            estado="PENDIENTE",
            fecha_vencimiento=payload.fecha_vencimiento,
            descripcion=payload.descripcion,
        )
        db.add(cuenta)
        await db.commit()
        await db.refresh(cuenta)
        return cuenta

    async def registrar_cobro(self, db: AsyncSession, payload: CobroCreate) -> Cobro:
        cuenta = await db.get(CuentaPorCobrar, payload.cuenta_cobrar_id)
        if not cuenta:
            raise HTTPException(status_code=404, detail="Cuenta por cobrar no encontrada")
        if payload.monto > cuenta.saldo:
            raise HTTPException(status_code=400, detail="Monto excede saldo pendiente")
        cobro = Cobro(**payload.model_dump())
        db.add(cobro)
        cuenta.saldo -= payload.monto
        if cuenta.saldo == 0:
            cuenta.estado = "PAGADO"
        elif cuenta.saldo < cuenta.monto:
            cuenta.estado = "PARCIAL"
        stmt = select(Caja).where(Caja.codigo == "CAJA-PRINCIPAL")
        caja = (await db.execute(stmt)).scalar_one_or_none()
        if caja:
            caja.saldo += payload.monto
            db.add(MovimientoCaja(caja_id=caja.id, tipo="INGRESO", monto=payload.monto, referencia=f"COBRO-{cobro.id if cobro.id else 'NEW'}", observaciones="Cobro registrado"))
        await db.commit()
        await db.refresh(cobro)
        return cobro

    async def registrar_pago(self, db: AsyncSession, payload: PagoCreate) -> Pago:
        cuenta = await db.get(CuentaPorPagar, payload.cuenta_pagar_id)
        if not cuenta:
            raise HTTPException(status_code=404, detail="Cuenta por pagar no encontrada")
        if payload.monto > cuenta.saldo:
            raise HTTPException(status_code=400, detail="Monto excede saldo pendiente")
        pago = Pago(**payload.model_dump())
        db.add(pago)
        cuenta.saldo -= payload.monto
        if cuenta.saldo == 0:
            cuenta.estado = "PAGADO"
        elif cuenta.saldo < cuenta.monto:
            cuenta.estado = "PARCIAL"
        await db.commit()
        await db.refresh(pago)
        return pago

    async def listar_cajas(self, db: AsyncSession):
        return list((await db.execute(select(Caja))).scalars().all())

    async def crear_caja(self, db: AsyncSession, payload: CajaCreate) -> Caja:
        caja = Caja(**payload.model_dump())
        db.add(caja)
        await db.commit()
        await db.refresh(caja)
        return caja

    async def actualizar_caja(self, db: AsyncSession, caja_id: int, payload: CajaUpdate) -> Caja:
        caja = await db.get(Caja, caja_id)
        if not caja:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(caja, k, v)
        await db.commit()
        await db.refresh(caja)
        return caja

    async def eliminar_caja(self, db: AsyncSession, caja_id: int) -> None:
        caja = await db.get(Caja, caja_id)
        if not caja:
            raise HTTPException(status_code=404, detail="Caja no encontrada")
        await db.delete(caja)
        await db.commit()

    async def listar_bancos(self, db: AsyncSession):
        return list((await db.execute(select(Banco))).scalars().all())

    async def crear_banco(self, db: AsyncSession, payload: BancoCreate) -> Banco:
        banco = Banco(**payload.model_dump())
        db.add(banco)
        await db.commit()
        await db.refresh(banco)
        return banco

    async def actualizar_banco(self, db: AsyncSession, banco_id: int, payload: BancoUpdate) -> Banco:
        banco = await db.get(Banco, banco_id)
        if not banco:
            raise HTTPException(status_code=404, detail="Banco no encontrado")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(banco, k, v)
        await db.commit()
        await db.refresh(banco)
        return banco

    async def eliminar_banco(self, db: AsyncSession, banco_id: int) -> None:
        banco = await db.get(Banco, banco_id)
        if not banco:
            raise HTTPException(status_code=404, detail="Banco no encontrado")
        await db.delete(banco)
        await db.commit()

    async def movimientos_caja(self, db: AsyncSession):
        return list((await db.execute(select(MovimientoCaja).order_by(MovimientoCaja.id.desc()))).scalars().all())

    async def movimientos_bancarios(self, db: AsyncSession):
        return list((await db.execute(select(MovimientoBancario).order_by(MovimientoBancario.id.desc()))).scalars().all())

    async def listar_cobros(self, db: AsyncSession):
        return list((await db.execute(select(Cobro).order_by(Cobro.id.desc()))).scalars().all())

    async def listar_pagos(self, db: AsyncSession):
        return list((await db.execute(select(Pago).order_by(Pago.id.desc()))).scalars().all())


finanzas_service = FinanzasService()
