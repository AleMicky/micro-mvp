from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.crud.usuario import crud_usuario
from app.schemas.usuario import AsignarRolesRequest, UsuarioCreate, UsuarioResponse, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioResponse])
async def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = False,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_USUARIOS_VER")),
):
    return await crud_usuario.get_all(db, skip=skip, limit=limit, solo_activos=solo_activos)


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_USUARIOS_VER")),
):
    usuario = await crud_usuario.get(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    payload: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_USUARIOS_CREAR")),
):
    if await crud_usuario.get_by_username(db, payload.nombre_usuario):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado",
        )
    if await crud_usuario.get_by_email(db, str(payload.correo)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    return await crud_usuario.create(db, payload)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_USUARIOS_CREAR")),
):
    usuario = await crud_usuario.get(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return await crud_usuario.update(db, usuario, payload)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_USUARIOS_CREAR")),
):
    usuario = await crud_usuario.get(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    await crud_usuario.soft_delete(db, usuario)


@router.post("/{usuario_id}/roles", response_model=UsuarioResponse)
async def asignar_roles_usuario(
    usuario_id: int,
    payload: AsignarRolesRequest,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permissions("AUTH_ROLES_GESTIONAR")),
):
    usuario = await crud_usuario.get(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return await crud_usuario.add_roles(db, usuario, payload.rol_ids)
