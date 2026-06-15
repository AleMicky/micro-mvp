from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.schemas.rol import RolCreate, RolUpdate


class CRUDRol(CRUDBase[Rol, RolCreate, RolUpdate]):
    async def get(self, db: AsyncSession, id: int) -> Rol | None:
        stmt = (
            select(Rol)
            .options(selectinload(Rol.permisos))
            .where(Rol.id == id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        solo_activos: bool = False,
    ) -> list[Rol]:
        stmt = select(Rol).options(selectinload(Rol.permisos))
        if solo_activos:
            stmt = stmt.where(Rol.activo.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_codigo(self, db: AsyncSession, codigo: str) -> Rol | None:
        stmt = (
            select(Rol)
            .options(selectinload(Rol.permisos))
            .where(Rol.codigo == codigo)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def assign_permisos(
        self, db: AsyncSession, rol: Rol, permiso_ids: list[int]
    ) -> Rol:
        permisos = []
        for permiso_id in permiso_ids:
            permiso = await db.get(Permiso, permiso_id)
            if permiso and permiso.activo:
                permisos.append(permiso)
        rol.permisos = permisos
        await db.commit()
        return await self.get(db, rol.id)  # type: ignore[arg-type]

    async def add_permisos(
        self, db: AsyncSession, rol: Rol, permiso_ids: list[int]
    ) -> Rol:
        permisos_actuales = {permiso.id for permiso in rol.permisos}
        for permiso_id in permiso_ids:
            if permiso_id in permisos_actuales:
                continue
            permiso = await db.get(Permiso, permiso_id)
            if permiso and permiso.activo:
                rol.permisos.append(permiso)
        await db.commit()
        return await self.get(db, rol.id)  # type: ignore[arg-type]


crud_rol = CRUDRol(Rol)
