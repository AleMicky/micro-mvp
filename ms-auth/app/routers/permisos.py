from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.crud.permiso import crud_permiso
from app.schemas.permiso import PermisoResponse

router = APIRouter(prefix="/permisos", tags=["permisos"])


@router.get("", response_model=list[PermisoResponse])
async def listar_permisos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    return await crud_permiso.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)


@router.get("/{permiso_id}", response_model=PermisoResponse)
async def obtener_permiso(
    permiso_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    permiso = await crud_permiso.get(db, permiso_id)
    if not permiso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permiso no encontrado")
    return permiso
