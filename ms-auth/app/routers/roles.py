from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.crud.rol import crud_rol
from app.schemas.rol import AsignarPermisosRequest, RolCreate, RolResponse, RolUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RolResponse])
async def listar_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    return await crud_rol.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)


@router.get("/{rol_id}", response_model=RolResponse)
async def obtener_rol(
    rol_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    rol = await crud_rol.get(db, rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return rol


@router.post("", response_model=RolResponse, status_code=status.HTTP_201_CREATED)
async def crear_rol(
    payload: RolCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    if await crud_rol.get_by_codigo(db, payload.codigo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de rol ya existe",
        )
    return await crud_rol.create(db, payload)


@router.put("/{rol_id}", response_model=RolResponse)
async def actualizar_rol(
    rol_id: int,
    payload: RolUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    rol = await crud_rol.get(db, rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return await crud_rol.update(db, rol, payload)


@router.delete("/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_rol(
    rol_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    rol = await crud_rol.get(db, rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    rol.activo = False
    await db.commit()


@router.post("/{rol_id}/permisos", response_model=RolResponse)
async def asignar_permisos_rol(
    rol_id: int,
    payload: AsignarPermisosRequest,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    rol = await crud_rol.get(db, rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return await crud_rol.add_permisos(db, rol, payload.permiso_ids)
