from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import Compania, Sucursal
from app.schemas.company import CompaniaCreate, CompaniaUpdate, SucursalCreate, SucursalUpdate


class CRUDCompania(CRUDBase[Compania, CompaniaCreate, CompaniaUpdate]):
    pass


class CRUDSucursal(CRUDBase[Sucursal, SucursalCreate, SucursalUpdate]):
    async def get_by_compania(self, db: AsyncSession, compania_id: int) -> list[Sucursal]:
        stmt = (
            select(Sucursal)
            .where(Sucursal.compania_id == compania_id)
            .options(selectinload(Sucursal.ciudad), selectinload(Sucursal.compania))
            .order_by(Sucursal.id)
        )
        return list((await db.execute(stmt)).scalars().all())


crud_compania = CRUDCompania(Compania)
crud_sucursal = CRUDSucursal(Sucursal)
