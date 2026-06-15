from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.permiso import Permiso
from app.schemas.permiso import PermisoCreate, PermisoUpdate


class CRUDPermiso(CRUDBase[Permiso, PermisoCreate, PermisoUpdate]):
    async def get_by_codigo(self, db: AsyncSession, codigo: str) -> Permiso | None:
        stmt = select(Permiso).where(Permiso.codigo == codigo)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


crud_permiso = CRUDPermiso(Permiso)
