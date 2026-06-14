from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.existencia import crud_existencia
from app.schemas.existencia import ExistenciaResponse

router = APIRouter(prefix="/existencias", tags=["existencias"])


@router.get("", response_model=list[ExistenciaResponse])
async def listar_existencias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud_existencia.get_all(db, skip=skip, limit=limit)


@router.get("/producto/{producto_id}", response_model=list[ExistenciaResponse])
async def listar_existencias_por_producto(
    producto_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud_existencia.get_all(
        db, skip=skip, limit=limit, producto_id=producto_id
    )


@router.get("/almacen/{almacen_id}", response_model=list[ExistenciaResponse])
async def listar_existencias_por_almacen(
    almacen_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await crud_existencia.get_all(
        db, skip=skip, limit=limit, almacen_id=almacen_id
    )


@router.get(
    "/producto/{producto_id}/almacen/{almacen_id}",
    response_model=ExistenciaResponse,
)
async def obtener_existencia_producto_almacen(
    producto_id: int,
    almacen_id: int,
    db: AsyncSession = Depends(get_db),
):
    existencia = await crud_existencia.get_by_producto_almacen(
        db, producto_id=producto_id, almacen_id=almacen_id
    )
    if not existencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Existencia no encontrada")
    return existencia
