import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.models import Banco, Caja, Cobro, CuentaBancaria, CuentaPorCobrar, CuentaPorPagar, Pago

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
            db.add(CuentaPorCobrar(codigo="CXC-00001", tercero_id=1, tercero_tipo="CLIENTE", monto=Decimal("1200"), saldo=Decimal("1200"), estado="PENDIENTE", descripcion="Venta demo 1"))
            db.add(CuentaPorCobrar(codigo="CXC-00002", tercero_id=2, tercero_tipo="CLIENTE", monto=Decimal("800"), saldo=Decimal("400"), estado="PARCIAL", descripcion="Venta demo 2"))
            await db.commit()

        if not (await db.execute(select(CuentaPorPagar).where(CuentaPorPagar.codigo == "CXP-00001"))).scalar_one_or_none():
            db.add(CuentaPorPagar(codigo="CXP-00001", tercero_id=1, tercero_tipo="PROVEEDOR", monto=Decimal("1500"), saldo=Decimal("1500"), estado="PENDIENTE", descripcion="OC demo 1"))
            db.add(CuentaPorPagar(codigo="CXP-00002", tercero_id=2, tercero_tipo="PROVEEDOR", monto=Decimal("800"), saldo=Decimal("0"), estado="PAGADO", descripcion="OC demo 2 pagada"))
            await db.commit()

        if not (await db.execute(select(Cobro).limit(1))).scalar_one_or_none():
            cxc = (await db.execute(select(CuentaPorCobrar).where(CuentaPorCobrar.codigo == "CXC-00002"))).scalar_one()
            db.add(Cobro(cuenta_cobrar_id=cxc.id, monto=Decimal("400"), metodo="EFECTIVO", fecha="2026-06-01"))
            db.add(Cobro(cuenta_cobrar_id=cxc.id, monto=Decimal("200"), metodo="TRANSFERENCIA", fecha="2026-06-05"))
            await db.commit()

        if not (await db.execute(select(Pago).limit(1))).scalar_one_or_none():
            cxp = (await db.execute(select(CuentaPorPagar).where(CuentaPorPagar.codigo == "CXP-00002"))).scalar_one()
            db.add(Pago(cuenta_pagar_id=cxp.id, monto=Decimal("500"), metodo="TRANSFERENCIA", fecha="2026-06-02"))
            db.add(Pago(cuenta_pagar_id=cxp.id, monto=Decimal("300"), metodo="TRANSFERENCIA", fecha="2026-06-08"))
            await db.commit()

    logger.info("Seed ms-finanzas completado")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())
