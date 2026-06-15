from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    refresh_token_expiration,
    verify_password,
)
from app.crud.refresh_token import crud_refresh_token
from app.crud.usuario import crud_usuario
from app.models.sesion_login import SesionLogin
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.usuario import UsuarioCreate


class AuthService:
    @staticmethod
    def _build_token_response(usuario: Usuario, refresh_token: str) -> TokenResponse:
        roles = crud_usuario.get_role_codes(usuario)
        permisos = crud_usuario.get_permission_codes(usuario)
        access_token = create_access_token(
            user_id=usuario.id,
            nombre_usuario=usuario.nombre_usuario,
            correo=usuario.correo,
            roles=roles,
            permisos=permisos,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    @staticmethod
    async def _registrar_sesion(
        db: AsyncSession,
        *,
        usuario_id: int | None,
        request: Request,
        exito: bool,
        mensaje: str,
    ) -> None:
        db.add(
            SesionLogin(
                usuario_id=usuario_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                exito=exito,
                mensaje=mensaje,
            )
        )
        await db.commit()

    async def login(
        self, db: AsyncSession, payload: LoginRequest, request: Request
    ) -> TokenResponse:
        usuario = await crud_usuario.get_by_username_or_email(db, payload.identificador)
        if not usuario or not verify_password(payload.password, usuario.password_hash):
            await self._registrar_sesion(
                db,
                usuario_id=usuario.id if usuario else None,
                request=request,
                exito=False,
                mensaje="Credenciales inválidas",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        if not usuario.activo:
            await self._registrar_sesion(
                db,
                usuario_id=usuario.id,
                request=request,
                exito=False,
                mensaje="Usuario inactivo",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo",
            )

        refresh_token = generate_refresh_token()
        await crud_refresh_token.create(
            db,
            usuario_id=usuario.id,
            token=refresh_token,
            expiracion_en=refresh_token_expiration(),
        )
        await crud_usuario.update_last_login(db, usuario)
        await self._registrar_sesion(
            db,
            usuario_id=usuario.id,
            request=request,
            exito=True,
            mensaje="Login exitoso",
        )

        usuario = await crud_usuario.get(db, usuario.id)
        return self._build_token_response(usuario, refresh_token)  # type: ignore[arg-type]

    async def register(
        self, db: AsyncSession, payload: RegisterRequest
    ) -> TokenResponse:
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

        usuario_in = UsuarioCreate(
            nombre_completo=payload.nombre_completo,
            nombre_usuario=payload.nombre_usuario,
            correo=str(payload.correo),
            password=payload.password,
        )
        usuario = await crud_usuario.create(db, usuario_in)

        refresh_token = generate_refresh_token()
        await crud_refresh_token.create(
            db,
            usuario_id=usuario.id,
            token=refresh_token,
            expiracion_en=refresh_token_expiration(),
        )
        return self._build_token_response(usuario, refresh_token)

    async def refresh(self, db: AsyncSession, refresh_token: str) -> TokenResponse:
        stored = await crud_refresh_token.get_valid(db, refresh_token)
        if not stored:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado",
            )

        usuario = await crud_usuario.get(db, stored.usuario_id)
        if not usuario or not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no válido",
            )

        await crud_refresh_token.revoke(db, stored)

        new_refresh_token = generate_refresh_token()
        await crud_refresh_token.create(
            db,
            usuario_id=usuario.id,
            token=new_refresh_token,
            expiracion_en=refresh_token_expiration(),
        )
        return self._build_token_response(usuario, new_refresh_token)

    async def logout(self, db: AsyncSession, refresh_token: str, user_id: int) -> None:
        stored = await crud_refresh_token.get_valid(db, refresh_token, user_id)
        if not stored:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token no válido",
            )
        await crud_refresh_token.revoke(db, stored)


auth_service = AuthService()
