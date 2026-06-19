"""
Seed idempotente para datos iniciales de ms-catalogos.

Ejecución manual:
    python -m app.seed
"""

import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.crud.precio_producto import crud_precio_producto
from app.crud.producto import crud_producto
from app.models.categoria import Categoria
from app.models.marca import Marca
from app.models.producto import Producto
from app.models.unidad_medida import UnidadMedida
from app.schemas.categoria import CategoriaCreate
from app.schemas.marca import MarcaCreate
from app.schemas.producto import ProductoCreate
from app.schemas.unidad_medida import UnidadMedidaCreate

logger = logging.getLogger(__name__)

CATEGORIAS_SEED = [
    {"codigo": "CAT-LACTEOS", "nombre": "Lácteos", "descripcion": "Leche, queso y derivados lácteos"},
    {"codigo": "CAT-GRANOS", "nombre": "Granos", "descripcion": "Arroz, quinua y cereales"},
    {"codigo": "CAT-ACEITES", "nombre": "Aceites", "descripcion": "Aceites comestibles"},
    {"codigo": "CAT-ENDULZANTES", "nombre": "Endulzantes", "descripcion": "Azúcar, miel y edulcorantes"},
    {"codigo": "CAT-CONSERVAS", "nombre": "Conservas", "descripcion": "Salsas, mayonesa y enlatados"},
    {"codigo": "CAT-LIMPIEZA", "nombre": "Limpieza", "descripcion": "Productos de limpieza del hogar"},
    {"codigo": "CAT-BEBIDAS", "nombre": "Bebidas", "descripcion": "Gaseosas, jugos y bebidas"},
    {"codigo": "CAT-PANADERIA", "nombre": "Panadería", "descripcion": "Pan, galletas y repostería"},
]

MARCAS_SEED = [
    {"codigo": "MAR-PIL", "nombre": "PIL", "descripcion": "Lácteos PIL"},
    {"codigo": "MAR-GRANO-ORO", "nombre": "Grano de Oro", "descripcion": "Arroz y granos"},
    {"codigo": "MAR-FINO", "nombre": "Fino", "descripcion": "Aceites Fino"},
    {"codigo": "MAR-GUABIRA", "nombre": "Guabirá", "descripcion": "Azúcar Guabirá"},
    {"codigo": "MAR-CRIS", "nombre": "Cris", "descripcion": "Salsas y mayonesa Cris"},
    {"codigo": "MAR-COCA-COLA", "nombre": "Coca-Cola", "descripcion": "Bebidas Coca-Cola"},
    {"codigo": "MAR-OMO", "nombre": "OMO", "descripcion": "Detergentes OMO"},
    {"codigo": "MAR-PRINCESA", "nombre": "Princesa", "descripcion": "Panadería Princesa"},
]

UNIDADES_SEED = [
    {"codigo": "UND", "nombre": "Unidad", "abreviatura": "UND"},
    {"codigo": "BOL", "nombre": "Bolsa", "abreviatura": "BOL"},
    {"codigo": "LT", "nombre": "Litro", "abreviatura": "LT"},
    {"codigo": "KG", "nombre": "Kilogramo", "abreviatura": "KG"},
    {"codigo": "CJ", "nombre": "Caja", "abreviatura": "CJ"},
    {"codigo": "PQT", "nombre": "Paquete", "abreviatura": "PQT"},
]

PRODUCTOS_SEED = [
    {
        "codigo": "PROD-001",
        "codigo_barras": "777100100001",
        "nombre": "Leche PIL 980cc",
        "descripcion": "Leche entera pasteurizada bolsa 980cc",
        "categoria_codigo": "CAT-LACTEOS",
        "marca_codigo": "MAR-PIL",
        "unidad_codigo": "BOL",
        "precio_venta": Decimal("18.50"),
    },
    {
        "codigo": "PROD-002",
        "codigo_barras": "777100100002",
        "nombre": "Arroz Grano de Oro 1kg",
        "descripcion": "Arroz blanco de grano largo bolsa 1kg",
        "categoria_codigo": "CAT-GRANOS",
        "marca_codigo": "MAR-GRANO-ORO",
        "unidad_codigo": "KG",
        "precio_venta": Decimal("12.00"),
    },
    {
        "codigo": "PROD-003",
        "codigo_barras": "777100100003",
        "nombre": "Aceite Fino 1L",
        "descripcion": "Aceite vegetal comestible botella 1 litro",
        "categoria_codigo": "CAT-ACEITES",
        "marca_codigo": "MAR-FINO",
        "unidad_codigo": "LT",
        "precio_venta": Decimal("16.50"),
    },
    {
        "codigo": "PROD-004",
        "codigo_barras": "777100100004",
        "nombre": "Azúcar Guabirá 1kg",
        "descripcion": "Azúcar blanca refinada bolsa 1kg",
        "categoria_codigo": "CAT-ENDULZANTES",
        "marca_codigo": "MAR-GUABIRA",
        "unidad_codigo": "KG",
        "precio_venta": Decimal("10.00"),
    },
    {
        "codigo": "PROD-005",
        "codigo_barras": "777100100005",
        "nombre": "Mayonesa Cris 120g",
        "descripcion": "Mayonesa tradicional frasco 120g",
        "categoria_codigo": "CAT-CONSERVAS",
        "marca_codigo": "MAR-CRIS",
        "unidad_codigo": "UND",
        "precio_venta": Decimal("2.00"),
    },
    {
        "codigo": "PROD-006",
        "codigo_barras": "777100100006",
        "nombre": "Coca-Cola 2L",
        "descripcion": "Bebida gaseosa sabor cola botella 2 litros",
        "categoria_codigo": "CAT-BEBIDAS",
        "marca_codigo": "MAR-COCA-COLA",
        "unidad_codigo": "UND",
        "precio_venta": Decimal("12.50"),
    },
]


async def _get_by_codigo(db, model, codigo: str):
    stmt = select(model).where(model.codigo == codigo)
    return (await db.execute(stmt)).scalar_one_or_none()


async def _ensure_categoria(db, data: dict) -> Categoria:
    categoria = await _get_by_codigo(db, Categoria, data["codigo"])
    if categoria:
        categoria.nombre = data["nombre"]
        categoria.descripcion = data.get("descripcion")
        await db.flush()
        logger.info("Categoría ya existe: %s", data["codigo"])
        return categoria
    categoria = Categoria(**CategoriaCreate(**data).model_dump())
    db.add(categoria)
    await db.flush()
    logger.info("Categoría creada: %s", data["nombre"])
    return categoria


async def _ensure_marca(db, data: dict) -> Marca:
    marca = await _get_by_codigo(db, Marca, data["codigo"])
    if marca:
        marca.nombre = data["nombre"]
        marca.descripcion = data.get("descripcion")
        await db.flush()
        logger.info("Marca ya existe: %s", data["codigo"])
        return marca
    marca = Marca(**MarcaCreate(**data).model_dump())
    db.add(marca)
    await db.flush()
    logger.info("Marca creada: %s", data["nombre"])
    return marca


async def _ensure_unidad(db, data: dict) -> UnidadMedida:
    unidad = await _get_by_codigo(db, UnidadMedida, data["codigo"])
    if unidad:
        unidad.nombre = data["nombre"]
        unidad.abreviatura = data["abreviatura"]
        await db.flush()
        logger.info("Unidad ya existe: %s", data["codigo"])
        return unidad
    unidad = UnidadMedida(**UnidadMedidaCreate(**data).model_dump())
    db.add(unidad)
    await db.flush()
    logger.info("Unidad creada: %s", data["nombre"])
    return unidad


async def _ensure_producto(
    db,
    data: dict,
    *,
    categoria: Categoria,
    marca: Marca,
    unidad: UnidadMedida,
) -> Producto:
    producto = await _get_by_codigo(db, Producto, data["codigo"])
    precio_venta = data["precio_venta"]

    if producto:
        producto.codigo_barras = data["codigo_barras"]
        producto.nombre = data["nombre"]
        producto.descripcion = data["descripcion"]
        producto.categoria_id = categoria.id
        producto.marca_id = marca.id
        producto.unidad_medida_id = unidad.id
        producto.precio_base = precio_venta
        await db.flush()
        logger.info("Producto ya existe: %s", data["codigo"])
        precio = await crud_precio_producto.get_activo(db, producto.id)
        if not precio:
            await crud_precio_producto.crear_precio_inicial(db, producto.id, precio_venta)
            logger.info("Precio inicial creado para producto: %s", data["codigo"])
        return producto

    payload = ProductoCreate(
        codigo=data["codigo"],
        codigo_barras=data["codigo_barras"],
        nombre=data["nombre"],
        descripcion=data["descripcion"],
        categoria_id=categoria.id,
        marca_id=marca.id,
        unidad_medida_id=unidad.id,
        precio_base=precio_venta,
        precio_venta=precio_venta,
    )
    producto = await crud_producto.create(db, payload)
    await crud_precio_producto.crear_precio_inicial(db, producto.id, precio_venta)
    logger.info("Producto creado: %s", data["nombre"])
    return producto


async def run_seed() -> None:
    async with async_session() as db:
        categorias: dict[str, Categoria] = {}
        for data in CATEGORIAS_SEED:
            categorias[data["codigo"]] = await _ensure_categoria(db, data)

        marcas: dict[str, Marca] = {}
        for data in MARCAS_SEED:
            marcas[data["codigo"]] = await _ensure_marca(db, data)

        unidades: dict[str, UnidadMedida] = {}
        for data in UNIDADES_SEED:
            unidades[data["codigo"]] = await _ensure_unidad(db, data)

        await db.commit()

        for data in PRODUCTOS_SEED:
            await _ensure_producto(
                db,
                data,
                categoria=categorias[data["categoria_codigo"]],
                marca=marcas[data["marca_codigo"]],
                unidad=unidades[data["unidad_codigo"]],
            )

    logger.info("Seed de ms-catalogos completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
