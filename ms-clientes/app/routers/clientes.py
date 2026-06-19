from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.cliente import (
    ClienteCreate,
    ClienteDetalleResponse,
    ClienteResponse,
    ClienteUpdate,
    HistorialClienteResponse,
    PuntosAsignarRequest,
    PuntosClienteResponse,
)
from app.services.cliente import cliente_service

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteResponse])
async def listar(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    return await cliente_service.get_all(db, skip=skip, limit=limit)


@router.get("/{cliente_id}", response_model=ClienteDetalleResponse)
async def obtener(cliente_id: int, db: AsyncSession = Depends(get_db)):
    obj = await cliente_service.get(db, cliente_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    total = await cliente_service.total_puntos(db, cliente_id)
    return ClienteDetalleResponse(
        **ClienteResponse.model_validate(obj).model_dump(),
        total_puntos=total,
        historial=[HistorialClienteResponse.model_validate(h) for h in obj.historial],
    )


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def crear(payload: ClienteCreate, db: AsyncSession = Depends(get_db)):
    return await cliente_service.create(db, payload)


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def actualizar(cliente_id: int, payload: ClienteUpdate, db: AsyncSession = Depends(get_db)):
    obj = await cliente_service.get(db, cliente_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return await cliente_service.update(db, obj, payload)


@router.get("/{cliente_id}/historial", response_model=list[HistorialClienteResponse])
async def historial(cliente_id: int, db: AsyncSession = Depends(get_db)):
    obj = await cliente_service.get(db, cliente_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    items = await cliente_service.get_historial(db, cliente_id)
    return [HistorialClienteResponse.model_validate(h) for h in items]


@router.post("/{cliente_id}/puntos", response_model=PuntosClienteResponse, status_code=status.HTTP_201_CREATED)
async def asignar_puntos(cliente_id: int, payload: PuntosAsignarRequest, db: AsyncSession = Depends(get_db)):
    registro = await cliente_service.asignar_puntos(db, cliente_id, payload)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return registro
