from collections.abc import Callable
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.crud.usuario import crud_usuario

security_scheme = HTTPBearer(auto_error=False)


@dataclass
class TokenPayload:
    user_id: int
    nombre_usuario: str
    correo: str
    roles: list[str]
    permisos: list[str]


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> TokenPayload:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return TokenPayload(
        user_id=int(payload["sub"]),
        nombre_usuario=payload["nombre_usuario"],
        correo=payload["correo"],
        roles=payload.get("roles", []),
        permisos=payload.get("permisos", []),
    )


async def get_current_active_user(
    payload: TokenPayload = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db),
):
    usuario = await crud_usuario.get(db, payload.user_id)
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo o no encontrado",
        )
    return usuario


def require_roles(*roles_requeridos: str) -> Callable:
    async def dependency(payload: TokenPayload = Depends(get_current_user_payload)) -> TokenPayload:
        if not any(rol in payload.roles for rol in roles_requeridos):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene los roles necesarios para esta operación",
            )
        return payload

    return dependency


def require_permissions(*permisos_requeridos: str) -> Callable:
    async def dependency(payload: TokenPayload = Depends(get_current_user_payload)) -> TokenPayload:
        if not any(permiso in payload.permisos for permiso in permisos_requeridos):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene los permisos necesarios para esta operación",
            )
        return payload

    return dependency
