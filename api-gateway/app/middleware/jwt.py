import re

import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

PUBLIC_ROUTES = {
    ("GET", "/health"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/register"),
}

PROTECTED_PREFIXES = (
    "/catalogos",
    "/inventario",
    "/compras",
    "/ventas",
    "/finanzas",
    "/reportes",
    "/companias",
    "/sucursales",
    "/clientes",
    "/notificaciones",
)
PROTECTED_AUTH_PATHS = (
    "/auth/me",
    "/auth/logout",
    "/auth/usuarios",
    "/auth/roles",
    "/auth/permisos",
)


def _requires_auth(method: str, path: str) -> bool:
    if method == "OPTIONS":
        return False
    if (method, path) in PUBLIC_ROUTES:
        return False
    if any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
        return True
    return any(
        path == protected or path.startswith(f"{protected}/")
        for protected in PROTECTED_AUTH_PATHS
    )


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    match = re.match(r"^Bearer\s+(.+)$", authorization, re.IGNORECASE)
    return match.group(1) if match else None


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        if not _requires_auth(method, path):
            return await call_next(request)

        token = _extract_bearer_token(request.headers.get("authorization"))
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token de acceso requerido"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except jwt.PyJWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token inválido o expirado"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user_id = payload.get("sub")
        request.state.roles = payload.get("roles", [])
        request.state.permisos = payload.get("permisos", [])

        return await call_next(request)
