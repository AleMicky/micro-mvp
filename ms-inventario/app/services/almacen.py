from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.company_client import company_client
from app.crud.almacen import crud_almacen
from app.models.almacen import Almacen
from app.schemas.almacen import (
    AlmacenCreate,
    AlmacenResponse,
    CompaniaSnapshot,
    SucursalSnapshot,
    AlmacenUpdate,
)


def almacen_to_response(almacen: Almacen) -> AlmacenResponse:
    response = AlmacenResponse.model_validate(almacen)
    if almacen.sucursal_id is not None:
        response.sucursal = SucursalSnapshot(
            id=almacen.sucursal_id,
            codigo=almacen.sucursal_codigo or "",
            nombre=almacen.sucursal_nombre or "",
        )
    if almacen.compania_id is not None:
        response.compania = CompaniaSnapshot(
            id=almacen.compania_id,
            nombre=almacen.compania_nombre or "",
        )
    return response


class AlmacenService:
    async def _aplicar_snapshot_sucursal(self, data: dict, sucursal_id: int) -> dict:
        snapshot = await company_client.obtener_sucursal_por_id(sucursal_id)
        data.update(snapshot)
        return data

    async def crear(self, db: AsyncSession, payload: AlmacenCreate) -> AlmacenResponse:
        data = payload.model_dump()
        sucursal_id = data.pop("sucursal_id", None)
        if sucursal_id is not None:
            await self._aplicar_snapshot_sucursal(data, sucursal_id)
        almacen = await crud_almacen.create_raw(db, data)
        return almacen_to_response(almacen)

    async def actualizar(
        self,
        db: AsyncSession,
        almacen: Almacen,
        payload: AlmacenUpdate,
    ) -> AlmacenResponse:
        data = payload.model_dump(exclude_unset=True)
        sucursal_id = data.pop("sucursal_id", None)

        if sucursal_id is not None and sucursal_id != almacen.sucursal_id:
            await self._aplicar_snapshot_sucursal(data, sucursal_id)
        elif sucursal_id is not None:
            data["sucursal_id"] = sucursal_id

        almacen = await crud_almacen.update_raw(db, almacen, data)
        return almacen_to_response(almacen)


almacen_service = AlmacenService()
