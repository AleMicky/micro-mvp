from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.events.publisher import publish_event
from app.models import Cliente, HistorialCliente, PuntosCliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, PuntosAsignarRequest


class ClienteService:
    async def get(self, db: AsyncSession, cliente_id: int) -> Cliente | None:
        stmt = (
            select(Cliente)
            .where(Cliente.id == cliente_id)
            .options(selectinload(Cliente.historial), selectinload(Cliente.puntos))
        )

        # print("Executing query>>>>:", stmt)  # Debugging line to print the query
        return (await db.execute(stmt)).scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Cliente]:
        stmt = select(Cliente).offset(skip).limit(limit).order_by(Cliente.id)
        return list((await db.execute(stmt)).scalars().all())

    async def create(self, db: AsyncSession, payload: ClienteCreate) -> Cliente:
        obj = Cliente(**payload.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        await publish_event("CustomerCreated", {"cliente_id": obj.id, "nombre": obj.nombre, "codigo": obj.codigo})
        return obj

    async def update(self, db: AsyncSession, obj: Cliente, payload: ClienteUpdate) -> Cliente:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await db.commit()
        await db.refresh(obj)
        await publish_event("CustomerUpdated", {"cliente_id": obj.id, "nombre": obj.nombre})
        return obj

    async def get_historial(self, db: AsyncSession, cliente_id: int) -> list[HistorialCliente]:
        stmt = (
            select(HistorialCliente)
            .where(HistorialCliente.cliente_id == cliente_id)
            .order_by(HistorialCliente.creado_en.desc())
        )
        return list((await db.execute(stmt)).scalars().all())

    async def asignar_puntos(self, db: AsyncSession, cliente_id: int, payload: PuntosAsignarRequest) -> PuntosCliente:
        cliente = await db.get(Cliente, cliente_id)
        if not cliente:
            return None  # type: ignore

        registro = PuntosCliente(
            cliente_id=cliente_id,
            puntos=payload.puntos,
            motivo=payload.motivo,
            referencia=payload.referencia,
        )
        db.add(registro)
        db.add(
            HistorialCliente(
                cliente_id=cliente_id,
                tipo="PUNTOS",
                descripcion=payload.motivo or "Puntos asignados",
                referencia=payload.referencia,
            )
        )
        await db.commit()
        await db.refresh(registro)
        await publish_event(
            "PointsAssigned",
            {"cliente_id": cliente_id, "puntos": payload.puntos, "referencia": payload.referencia},
        )
        return registro

    async def registrar_compra(
        self,
        db: AsyncSession,
        *,
        cliente_id: int,
        monto: Decimal,
        referencia: str,
        descripcion: str,
    ) -> None:
        db.add(
            HistorialCliente(
                cliente_id=cliente_id,
                tipo="COMPRA",
                descripcion=descripcion,
                monto=monto,
                referencia=referencia,
            )
        )
        await db.commit()

    async def total_puntos(self, db: AsyncSession, cliente_id: int) -> int:
        stmt = select(func.coalesce(func.sum(PuntosCliente.puntos), 0)).where(
            PuntosCliente.cliente_id == cliente_id, PuntosCliente.activo.is_(True)
        )
        return int((await db.execute(stmt)).scalar_one())


cliente_service = ClienteService()
