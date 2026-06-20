from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.almacen import Almacen
from app.schemas.almacen import AlmacenCreate, AlmacenUpdate


class CRUDAlmacen(CRUDBase[Almacen, AlmacenCreate, AlmacenUpdate]):
    async def create_raw(self, db: AsyncSession, data: dict) -> Almacen:
        obj = self.model(**data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update_raw(self, db: AsyncSession, db_obj: Almacen, data: dict) -> Almacen:
        for field, value in data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


crud_almacen = CRUDAlmacen(Almacen)
