"""
Seed idempotente para datos iniciales de ms-clientes.

Ejecución manual:
    python -m app.seed
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.database import async_session
from app.models import Cliente, PuntosCliente

logger = logging.getLogger(__name__)

CLIENTES_SEED = [
    {
        "codigo": "CLI-001",
        "nombre": "Juanito Pérez",
        "documento": "1234567",
        "email": "juanito.perez@test.com",
        "telefono": "70000001",
        "puntos": 0,
    },
    {
        "codigo": "CLI-WHATSAPP",
        "nombre": "Mostrador WhatsApp",
        "documento": "0",
        "email": None,
        "telefono": None,
        "puntos": 0,
    },
]


async def _ensure_cliente(db, data: dict) -> Cliente:
    stmt = select(Cliente).where(Cliente.codigo == data["codigo"])
    cliente = (await db.execute(stmt)).scalar_one_or_none()
    if cliente:
        logger.info("Cliente ya existe: %s", data["codigo"])
        return cliente

    cliente = Cliente(
        codigo=data["codigo"],
        nombre=data["nombre"],
        documento=data["documento"],
        email=data["email"],
        telefono=data["telefono"],
    )
    db.add(cliente)
    await db.flush()
    logger.info("Cliente creado: %s", data["nombre"])
    return cliente


async def _ensure_puntos_iniciales(db, cliente: Cliente, puntos: int) -> None:
    stmt = select(PuntosCliente).where(
        PuntosCliente.cliente_id == cliente.id,
        PuntosCliente.referencia == "SEED-INICIAL",
    )
    if (await db.execute(stmt)).scalar_one_or_none():
        logger.info("Puntos iniciales ya existen para: %s", cliente.codigo)
        return

    db.add(
        PuntosCliente(
            cliente_id=cliente.id,
            puntos=puntos,
            motivo="Saldo inicial",
            referencia="SEED-INICIAL",
        )
    )
    logger.info("Puntos iniciales registrados para: %s", cliente.codigo)


async def run_seed() -> None:
    async with async_session() as db:
        for data in CLIENTES_SEED:
            puntos = data["puntos"]
            cliente = await _ensure_cliente(db, {k: v for k, v in data.items() if k != "puntos"})
            await _ensure_puntos_iniciales(db, cliente, puntos)

        await db.commit()

    logger.info("Seed de ms-clientes completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
