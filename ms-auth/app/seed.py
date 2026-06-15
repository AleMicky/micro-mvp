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
    {"codigo": "OPERADOR", "nombre": "Operador", "descripcion": "Operaciones de catálogos e inventario"},
    {"codigo": "CONSULTA", "nombre": "Consulta", "descripcion": "Solo lectura"},
]

PERMISOS_SEED = [
    {"codigo": "CATALOGOS_VER", "nombre": "Ver catálogos", "modulo": "CATALOGOS"},
    {"codigo": "CATALOGOS_CREAR", "nombre": "Crear catálogos", "modulo": "CATALOGOS"},
    {"codigo": "CATALOGOS_EDITAR", "nombre": "Editar catálogos", "modulo": "CATALOGOS"},
    {"codigo": "CATALOGOS_ELIMINAR", "nombre": "Eliminar catálogos", "modulo": "CATALOGOS"},
    {"codigo": "INVENTARIO_VER", "nombre": "Ver inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_CREAR", "nombre": "Crear inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_EDITAR", "nombre": "Editar inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_ELIMINAR", "nombre": "Eliminar inventario", "modulo": "INVENTARIO"},
    {"codigo": "INVENTARIO_MOVIMIENTOS", "nombre": "Movimientos de inventario", "modulo": "INVENTARIO"},
    {"codigo": "AUTH_USUARIOS_VER", "nombre": "Ver usuarios", "modulo": "AUTH"},
    {"codigo": "AUTH_USUARIOS_CREAR", "nombre": "Gestionar usuarios", "modulo": "AUTH"},
    {"codigo": "AUTH_ROLES_GESTIONAR", "nombre": "Gestionar roles y permisos", "modulo": "AUTH"},
]

ROL_PERMISOS_SEED = {
    "ADMIN": [p["codigo"] for p in PERMISOS_SEED],
    "OPERADOR": [
        "CATALOGOS_VER",
        "CATALOGOS_CREAR",
        "INVENTARIO_VER",
        "INVENTARIO_CREAR",
        "INVENTARIO_MOVIMIENTOS",
    ],
    "CONSULTA": ["CATALOGOS_VER", "INVENTARIO_VER"],
}

ADMIN_USER = {
    "nombre_completo": "Administrador del Sistema",
    "nombre_usuario": "admin",
    "correo": "admin@test.com",
    "password": "Admin123456",
}


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


async def _ensure_admin_user(db, rol_admin: Rol) -> None:
    usuario = await crud_usuario.get_by_username(db, ADMIN_USER["nombre_usuario"])

    if not usuario:
        usuario = await crud_usuario.create(
            db,
            UsuarioCreate(
                nombre_completo=ADMIN_USER["nombre_completo"],
                nombre_usuario=ADMIN_USER["nombre_usuario"],
                correo=ADMIN_USER["correo"],
                password=ADMIN_USER["password"],
            ),
        )
        logger.info("Usuario admin creado: %s", ADMIN_USER["nombre_usuario"])
    else:
        logger.info("Usuario admin ya existe: %s", ADMIN_USER["nombre_usuario"])
        usuario = await crud_usuario.get(db, usuario.id)

    roles_actuales = {rol.id for rol in usuario.roles}
    if rol_admin.id not in roles_actuales:
        usuario.roles.append(rol_admin)
        await db.commit()
        logger.info("Rol ADMIN asignado al usuario admin")


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

        await _ensure_admin_user(db, roles_por_codigo["ADMIN"])

    logger.info("Seed de ms-auth completado")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    await run_seed()


if __name__ == "__main__":
    asyncio.run(main())
