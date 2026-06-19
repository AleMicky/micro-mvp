import logging

from sqlalchemy import select

from app.core.database import async_session
from app.models import Cliente

logger = logging.getLogger(__name__)


async def run_seed() -> None:
    async with async_session() as db:
        existing = await db.execute(select(Cliente).limit(1))
        if existing.scalar_one_or_none():
            logger.info("Seed ms-clientes ya aplicado, omitiendo")
            return

        cliente = Cliente(
            codigo="CLI-001",
            nombre="Juanito Pérez",
            email="juanito@email.com",
            telefono="71234567",
            documento="1234567",
            direccion="La Paz, Bolivia",
        )
        db.add(cliente)
        await db.commit()
        logger.info("Seed ms-clientes completado: Juanito Pérez")
