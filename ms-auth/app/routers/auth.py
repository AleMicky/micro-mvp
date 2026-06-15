from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_user_payload
from app.crud.usuario import crud_usuario
from app.models.usuario import Usuario
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.login(db, payload, request)


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.register(db, payload)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh(db, payload.refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    token_payload=Depends(get_current_user_payload),
):
    await auth_service.logout(db, payload.refresh_token, token_payload.user_id)


@router.get("/me", response_model=MeResponse)
async def me(usuario: Usuario = Depends(get_current_active_user)):
    return MeResponse(
        id=usuario.id,
        nombre_completo=usuario.nombre_completo,
        nombre_usuario=usuario.nombre_usuario,
        correo=usuario.correo,
        activo=usuario.activo,
        ultimo_login_en=usuario.ultimo_login_en,
        roles=crud_usuario.get_role_codes(usuario),
        permisos=crud_usuario.get_permission_codes(usuario),
        creado_en=usuario.creado_en,
        actualizado_en=usuario.actualizado_en,
    )
