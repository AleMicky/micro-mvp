"""
Seed idempotente para datos iniciales de ms-company.

Ejecución manual:
    python -m app.seed
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.database import async_session
from app.models import Ciudad, Compania, Sucursal

logger = logging.getLogger(__name__)

CIUDADES_SEED = [
    {"nombre": "Cochabamba", "departamento": "Cochabamba"},
    {"nombre": "La Paz", "departamento": "La Paz"},
    {"nombre": "Santa Cruz", "departamento": "Santa Cruz"},
    {"nombre": "Oruro", "departamento": "Oruro"},
]

COMPANIAS_SEED = [
    {
        "codigo": "SM-BOL",
        "nombre": "SuperMarket Bolivia",
        "nit": "102030405",
        "direccion": "Av. Heroínas 1200, Cochabamba",
        "telefono": "44221100",
    },
    {
        "codigo": "OXXO-BOL",
        "nombre": "OXXO Bolivia",
        "nit": "203040506",
        "direccion": "Av. Arce 2500, La Paz",
        "telefono": "22113344",
    },
    {
        "codigo": "HIPERMAXI-BOL",
        "nombre": "Hipermaxi",
        "nit": "304050607",
        "direccion": "Av. Cristo Redentor 8vo anillo, Santa Cruz",
        "telefono": "33445566",
    },
    {
        "codigo": "IC-NORTE-BOL",
        "nombre": "IC Norte",
        "nit": "405060708",
        "direccion": "Av. Banzer km 4, Santa Cruz",
        "telefono": "35667788",
    },
]

SUCURSALES_SEED = [
    {
        "codigo": "SUC-CENTRAL",
        "nombre": "Central",
        "compania_codigo": "SM-BOL",
        "ciudad_nombre": "Cochabamba",
        "direccion": "Calle Lanza esq. Ayacucho, Cochabamba",
    },
    {
        "codigo": "SUC-NORTE",
        "nombre": "Zona Norte",
        "compania_codigo": "SM-BOL",
        "ciudad_nombre": "Cochabamba",
        "direccion": "Av. América 3200, Cochabamba",
    },
    {
        "codigo": "SUC-PRADO",
        "nombre": "Sucursal Prado",
        "compania_codigo": "OXXO-BOL",
        "ciudad_nombre": "La Paz",
        "direccion": "Av. 16 de Julio, El Prado, La Paz",
    },
    {
        "codigo": "SUC-ALTO",
        "nombre": "Sucursal El Alto",
        "compania_codigo": "OXXO-BOL",
        "ciudad_nombre": "La Paz",
        "direccion": "Av. Juan Pablo II, El Alto",
    },
    {
        "codigo": "SUC-HIPER-1",
        "nombre": "Sucursal 1",
        "compania_codigo": "HIPERMAXI-BOL",
        "ciudad_nombre": "Santa Cruz",
        "direccion": "Av. Cristo Redentor, Santa Cruz",
    },
    {
        "codigo": "SUC-MELCHOR",
        "nombre": "Melchor Pérez",
        "compania_codigo": "IC-NORTE-BOL",
        "ciudad_nombre": "Santa Cruz",
        "direccion": "Av. Melchor Pérez de Olguín, Santa Cruz",
    },
]


async def _ensure_ciudad(db, data: dict) -> Ciudad:
    stmt = select(Ciudad).where(Ciudad.nombre == data["nombre"])
    ciudad = (await db.execute(stmt)).scalar_one_or_none()
    if ciudad:
        logger.info("Ciudad ya existe: %s", data["nombre"])
        return ciudad
    ciudad = Ciudad(**data)
    db.add(ciudad)
    await db.flush()
    logger.info("Ciudad creada: %s", data["nombre"])
    return ciudad


async def _ensure_compania(db, data: dict) -> Compania:
    stmt = select(Compania).where(Compania.codigo == data["codigo"])
    compania = (await db.execute(stmt)).scalar_one_or_none()
    if compania:
        logger.info("Compañía ya existe: %s", data["codigo"])
        return compania
    compania = Compania(**data)
    db.add(compania)
    await db.flush()
    logger.info("Compañía creada: %s", data["nombre"])
    return compania


async def _ensure_sucursal(
    db,
    data: dict,
    *,
    compania: Compania,
    ciudad: Ciudad,
) -> Sucursal:
    stmt = select(Sucursal).where(Sucursal.codigo == data["codigo"])
    sucursal = (await db.execute(stmt)).scalar_one_or_none()
    if sucursal:
        logger.info("Sucursal ya existe: %s", data["codigo"])
        return sucursal
    sucursal = Sucursal(
        codigo=data["codigo"],
        nombre=data["nombre"],
        compania_id=compania.id,
        ciudad_id=ciudad.id,
        direccion=data["direccion"],
    )
    db.add(sucursal)
    await db.flush()
    logger.info("Sucursal creada: %s", data["nombre"])
    return sucursal


async def run_seed() -> None:
    async with async_session() as db:
        ciudades_por_nombre: dict[str, Ciudad] = {}
        for data in CIUDADES_SEED:
            ciudad = await _ensure_ciudad(db, data)
            ciudades_por_nombre[data["nombre"]] = ciudad

        companias_por_codigo: dict[str, Compania] = {}
        for data in COMPANIAS_SEED:
            compania = await _ensure_compania(db, data)
            companias_por_codigo[data["codigo"]] = compania

        for data in SUCURSALES_SEED:
            await _ensure_sucursal(
                db,
                data,
                compania=companias_por_codigo[data["compania_codigo"]],
                ciudad=ciudades_por_nombre[data["ciudad_nombre"]],
            )

        await db.commit()

    logger.info("Seed de ms-company completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
