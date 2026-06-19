"""
Seed idempotente para datos iniciales de ms-auth.

Ejecución manual:
    python -m app.seed
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.database import async_session
from app.crud.permiso import crud_permiso
from app.crud.rol import crud_rol
from app.crud.usuario import crud_usuario
from app.models.asociaciones import RolPermiso
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.schemas.permiso import PermisoCreate
from app.schemas.rol import RolCreate
from app.schemas.usuario import UsuarioCreate

logger = logging.getLogger(__name__)

ROLES_SEED = [
    {"codigo": "ADMIN", "nombre": "Administrador", "descripcion": "Acceso total al sistema"},
    {"codigo": "GERENTE", "nombre": "Gerente", "descripcion": "Reportes, ventas, inventario y sucursales"},
    {"codigo": "CAJERO", "nombre": "Cajero", "descripcion": "Registro de ventas y clientes"},
    {"codigo": "ALMACENERO", "nombre": "Almacenero", "descripcion": "Gestión de inventario y transferencias"},
    {"codigo": "SUPERVISOR", "nombre": "Supervisor", "descripcion": "Revisión de stock, ventas y notificaciones"},
    {"codigo": "CONSULTA", "nombre": "Consulta", "descripcion": "Solo lectura"},
]

PERMISOS_SEED = [
    {"codigo": "AUTH_USUARIOS_VER", "nombre": "Ver usuarios", "modulo": "AUTH"},
    {"codigo": "AUTH_USUARIOS_CREAR", "nombre": "Crear usuarios", "modulo": "AUTH"},
    {"codigo": "AUTH_USUARIOS_EDITAR", "nombre": "Editar usuarios", "modulo": "AUTH"},
    {"codigo": "AUTH_USUARIOS_ELIMINAR", "nombre": "Eliminar usuarios", "modulo": "AUTH"},
    {"codigo": "AUTH_ROLES_VER", "nombre": "Ver roles", "modulo": "AUTH"},
    {"codigo": "AUTH_ROLES_GESTIONAR", "nombre": "Gestionar roles y permisos", "modulo": "AUTH"},
    {"codigo": "CATALOGOS_VER", "nombre": "Ver catálogos", "modulo": "CATALOGOS"},
    {"codigo": "CATALOGOS_CREAR", "nombre": "Crear catálogos", "modulo": "CATALOGOS"},
    {"codigo": "CATALOGOS_EDITAR", "nombre": "Editar catálogos", "modulo": "CATALOGOS"},
    {"codigo": "CATALOGOS_ELIMINAR", "nombre": "Eliminar catálogos", "modulo": "CATALOGOS"},
    {"codigo": "COMPANY_VER", "nombre": "Ver compañías", "modulo": "COMPANY"},
    {"codigo": "COMPANY_CREAR", "nombre": "Crear compañías", "modulo": "COMPANY"},
    {"codigo": "COMPANY_EDITAR", "nombre": "Editar compañías", "modulo": "COMPANY"},
    {"codigo": "COMPANY_ELIMINAR", "nombre": "Eliminar compañías", "modulo": "COMPANY"},
    {"codigo": "INVENTARIO_VER", "nombre": "Ver inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_CREAR", "nombre": "Crear inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_EDITAR", "nombre": "Editar inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_ELIMINAR", "nombre": "Eliminar inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_TRANSFERIR", "nombre": "Transferir inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_IMPORTAR_EXCEL", "nombre": "Importar inventario desde Excel", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_KARDEX", "nombre": "Ver kardex de inventario", "modulo": "INVENTARIO"},
    {"codigo": "CLIENTES_VER", "nombre": "Ver clientes", "modulo": "CLIENTES"},
    {"codigo": "CLIENTES_CREAR", "nombre": "Crear clientes", "modulo": "CLIENTES"},
    {"codigo": "CLIENTES_EDITAR", "nombre": "Editar clientes", "modulo": "CLIENTES"},
    {"codigo": "CLIENTES_ELIMINAR", "nombre": "Eliminar clientes", "modulo": "CLIENTES"},
    {"codigo": "CLIENTES_PUNTOS", "nombre": "Gestionar puntos de clientes", "modulo": "CLIENTES"},
    {"codigo": "VENTAS_VER", "nombre": "Ver ventas", "modulo": "VENTAS"},
    {"codigo": "VENTAS_CREAR", "nombre": "Crear ventas", "modulo": "VENTAS"},
    {"codigo": "VENTAS_CANCELAR", "nombre": "Cancelar ventas", "modulo": "VENTAS"},
    {"codigo": "VENTAS_FACTURAR", "nombre": "Facturar ventas", "modulo": "VENTAS"},
    {"codigo": "NOTIFICACIONES_VER", "nombre": "Ver notificaciones", "modulo": "NOTIFICACIONES"},
    {"codigo": "REPORTES_VER", "nombre": "Ver reportes", "modulo": "REPORTES"},
    {"codigo": "REPORTES_VENTAS", "nombre": "Reportes de ventas", "modulo": "REPORTES"},
    {"codigo": "REPORTES_INVENTARIO", "nombre": "Reportes de inventario", "modulo": "REPORTES"},
    {"codigo": "REPORTES_CLIENTES", "nombre": "Reportes de clientes", "modulo": "REPORTES"},
]

ROL_PERMISOS_SEED = {
    "ADMIN": [p["codigo"] for p in PERMISOS_SEED],
    "GERENTE": [
        "CATALOGOS_VER",
        "COMPANY_VER",
        "INVENTARIO_VER",
        "INVENTARIO_KARDEX",
        "CLIENTES_VER",
        "VENTAS_VER",
        "NOTIFICACIONES_VER",
        "REPORTES_VER",
        "REPORTES_VENTAS",
        "REPORTES_INVENTARIO",
        "REPORTES_CLIENTES",
    ],
    "CAJERO": [
        "CATALOGOS_VER",
        "INVENTARIO_VER",
        "CLIENTES_VER",
        "CLIENTES_CREAR",
        "CLIENTES_EDITAR",
        "VENTAS_VER",
        "VENTAS_CREAR",
        "VENTAS_FACTURAR",
    ],
    "ALMACENERO": [
        "CATALOGOS_VER",
        "INVENTARIO_VER",
        "INVENTARIO_CREAR",
        "INVENTARIO_EDITAR",
        "INVENTARIO_TRANSFERIR",
        "INVENTARIO_IMPORTAR_EXCEL",
        "INVENTARIO_KARDEX",
    ],
    "SUPERVISOR": [
        "CATALOGOS_VER",
        "COMPANY_VER",
        "INVENTARIO_VER",
        "INVENTARIO_KARDEX",
        "CLIENTES_VER",
        "VENTAS_VER",
        "NOTIFICACIONES_VER",
        "REPORTES_VER",
    ],
    "CONSULTA": [
        "CATALOGOS_VER",
        "COMPANY_VER",
        "INVENTARIO_VER",
        "CLIENTES_VER",
        "VENTAS_VER",
        "NOTIFICACIONES_VER",
    ],
}

USUARIOS_SEED = [
    {
        "nombre_completo": "Administrador del Sistema",
        "nombre_usuario": "admin",
        "correo": "admin@supermarket.bo",
        "password": "Admin123456",
        "rol_codigo": "ADMIN",
    },
    {
        "nombre_completo": "Gerente General",
        "nombre_usuario": "gerente",
        "correo": "gerente@supermarket.bo",
        "password": "Gerente123456",
        "rol_codigo": "GERENTE",
    },
    {
        "nombre_completo": "Cajero Principal",
        "nombre_usuario": "cajero",
        "correo": "cajero@supermarket.bo",
        "password": "Cajero123456",
        "rol_codigo": "CAJERO",
    },
    {
        "nombre_completo": "Responsable de Almacén",
        "nombre_usuario": "almacenero",
        "correo": "almacen@supermarket.bo",
        "password": "Almacen123456",
        "rol_codigo": "ALMACENERO",
    },
    {
        "nombre_completo": "Supervisor de Sucursal",
        "nombre_usuario": "supervisor",
        "correo": "supervisor@supermarket.bo",
        "password": "Supervisor123456",
        "rol_codigo": "SUPERVISOR",
    },
]


async def _ensure_permiso(db, data: dict) -> Permiso:
    permiso = await crud_permiso.get_by_codigo(db, data["codigo"])
    if permiso:
        logger.info("Permiso ya existe: %s", data["codigo"])
        return permiso
    permiso = await crud_permiso.create(db, PermisoCreate(**data))
    logger.info("Permiso creado: %s", data["codigo"])
    return permiso


async def _ensure_rol(db, data: dict) -> Rol:
    rol = await crud_rol.get_by_codigo(db, data["codigo"])
    if rol:
        logger.info("Rol ya existe: %s", data["codigo"])
        return rol
    rol = await crud_rol.create(db, RolCreate(**data))
    logger.info("Rol creado: %s", data["codigo"])
    return rol


async def _ensure_rol_permiso(db, rol: Rol, permiso: Permiso) -> None:
    stmt = select(RolPermiso).where(
        RolPermiso.rol_id == rol.id,
        RolPermiso.permiso_id == permiso.id,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return
    db.add(RolPermiso(rol_id=rol.id, permiso_id=permiso.id))
    logger.info("Permiso %s asignado a rol %s", permiso.codigo, rol.codigo)


async def _ensure_usuario(db, data: dict, rol: Rol) -> None:
    usuario = await crud_usuario.get_by_username(db, data["nombre_usuario"])

    if not usuario:
        usuario = await crud_usuario.create(
            db,
            UsuarioCreate(
                nombre_completo=data["nombre_completo"],
                nombre_usuario=data["nombre_usuario"],
                correo=data["correo"],
                password=data["password"],
            ),
        )
        logger.info("Usuario creado: %s", data["nombre_usuario"])
    else:
        logger.info("Usuario ya existe: %s", data["nombre_usuario"])
        usuario = await crud_usuario.get(db, usuario.id)

    roles_actuales = {r.id for r in usuario.roles}
    if rol.id not in roles_actuales:
        usuario.roles.append(rol)
        await db.commit()
        logger.info("Rol %s asignado al usuario %s", rol.codigo, data["nombre_usuario"])


async def run_seed() -> None:
    async with async_session() as db:
        permisos_por_codigo: dict[str, Permiso] = {}
        for data in PERMISOS_SEED:
            permiso = await _ensure_permiso(db, data)
            permisos_por_codigo[data["codigo"]] = permiso

        roles_por_codigo: dict[str, Rol] = {}
        for data in ROLES_SEED:
            rol = await _ensure_rol(db, data)
            roles_por_codigo[data["codigo"]] = rol

        for rol_codigo, permiso_codigos in ROL_PERMISOS_SEED.items():
            rol = roles_por_codigo[rol_codigo]
            for permiso_codigo in permiso_codigos:
                await _ensure_rol_permiso(db, rol, permisos_por_codigo[permiso_codigo])

        await db.commit()

        for data in USUARIOS_SEED:
            await _ensure_usuario(db, data, roles_por_codigo[data["rol_codigo"]])

    logger.info("Seed de ms-auth completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
