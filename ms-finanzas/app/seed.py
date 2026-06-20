import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.models import Banco, Caja, CuentaBancaria, CuentaPorCobrar, CuentaPorPagar

logger = logging.getLogger(__name__)


async def run_seed() -> None:
    async with async_session() as db:
        if not (await db.execute(select(Caja).where(Caja.codigo == "CAJA-PRINCIPAL"))).scalar_one_or_none():
            db.add(Caja(codigo="CAJA-PRINCIPAL", nombre="Caja Principal", saldo=Decimal("5000.00")))
            logger.info("Caja principal creada")

        if not (await db.execute(select(Banco).where(Banco.codigo == "BANCO-001"))).scalar_one_or_none():
            banco = Banco(codigo="BANCO-001", nombre="Banco Nacional Demo")
            db.add(banco)
            await db.flush()
            db.add(CuentaBancaria(banco_id=banco.id, numero_cuenta="1234567890", saldo=Decimal("25000.00")))
            logger.info("Banco demo creado")

        await db.commit()

        if not (await db.execute(select(CuentaPorCobrar).where(CuentaPorCobrar.codigo == "CXC-00001"))).scalar_one_or_none():
            db.add(
                CuentaPorCobrar(
                    codigo="CXC-00001",
                    tercero_id=1,
                    tercero_tipo="CLIENTE",
                    monto=Decimal("37.00"),
                    saldo=Decimal("37.00"),
                    estado="PENDIENTE",
                    descripcion="Venta demo leche PIL",
                )
            )
            await db.commit()

        if not (await db.execute(select(CuentaPorPagar).where(CuentaPorPagar.codigo == "CXP-00001"))).scalar_one_or_none():
            db.add(
                CuentaPorPagar(
                    codigo="CXP-00001",
                    tercero_id=1,
                    tercero_tipo="PROVEEDOR",
                    monto=Decimal("925.00"),
                    saldo=Decimal("925.00"),
                    estado="PENDIENTE",
                    descripcion="OC demo leche PIL",
                )
            )
            await db.commit()

    logger.info("Seed ms-finanzas completado")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())
