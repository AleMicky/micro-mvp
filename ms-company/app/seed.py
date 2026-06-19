import logging

from sqlalchemy import select

from app.core.database import async_session
from app.models import Ciudad, Compania, Sucursal

logger = logging.getLogger(__name__)


async def run_seed() -> None:
    async with async_session() as db:
        existing = await db.execute(select(Compania).limit(1))
        if existing.scalar_one_or_none():
            logger.info("Seed ms-company ya aplicado, omitiendo")
            return

        la_paz = Ciudad(nombre="La Paz", departamento="La Paz")
        scz = Ciudad(nombre="Santa Cruz", departamento="Santa Cruz")
        db.add_all([la_paz, scz])
        await db.flush()

        supermarket = Compania(
            codigo="SM-BOL",
            nombre="SuperMarket Bolivia",
            nit="123456789",
            direccion="Av. Principal 100",
            telefono="22112233",
        )
        oxxo = Compania(
            codigo="OXXO-BOL",
            nombre="OXXO Bolivia",
            nit="987654321",
            direccion="Zona Sur 200",
            telefono="33445566",
        )
        db.add_all([supermarket, oxxo])
        await db.flush()

        sucursales = [
            Sucursal(codigo="SUC-CENTRAL", nombre="Sucursal Central", compania_id=supermarket.id, ciudad_id=la_paz.id, direccion="Centro"),
            Sucursal(codigo="SUC-NORTE", nombre="Sucursal Zona Norte", compania_id=supermarket.id, ciudad_id=la_paz.id, direccion="Zona Norte"),
            Sucursal(codigo="SUC-PRADO", nombre="Sucursal Prado", compania_id=oxxo.id, ciudad_id=la_paz.id, direccion="El Prado"),
            Sucursal(codigo="SUC-ALTO", nombre="Sucursal El Alto", compania_id=oxxo.id, ciudad_id=la_paz.id, direccion="El Alto"),
        ]
        db.add_all(sucursales)
        await db.commit()
        logger.info("Seed ms-company completado")
