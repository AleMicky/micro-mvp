"""
Placeholder para validación JWT centralizada.

Cuando se implemente ms-auth, este middleware interceptará
las peticiones protegidas antes de reenviarlas a los microservicios.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class JWTPlaceholderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # MVP: sin validación. Rutas públicas pasan directo.
        # Futuro: validar Authorization header y adjuntar claims al request.
        return await call_next(request)
