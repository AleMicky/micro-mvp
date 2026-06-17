import httpx
from fastapi import APIRouter, Request, Response

from app.core.config import settings

router = APIRouter(tags=["proxy"])

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

AUTH_PATHS = {"login", "refresh", "logout", "me", "register"}


def _build_auth_target(path: str) -> str:
    first_segment = path.split("/")[0] if path else ""
    if first_segment in AUTH_PATHS:
        return f"{settings.ms_auth_url}/auth/{path}"
    return f"{settings.ms_auth_url}/{path}"


async def _proxy_request(target_url: str, request: Request) -> Response:
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "host"
    }

    body = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
        )

    response_headers = {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )


@router.api_route(
    "/catalogos/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_catalogos(path: str, request: Request) -> Response:
    target_url = f"{settings.ms_catalogos_url}/{path}"
    return await _proxy_request(target_url, request)


@router.api_route(
    "/inventario/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_inventario(path: str, request: Request) -> Response:
    target_url = f"{settings.ms_inventario_url}/{path}"
    return await _proxy_request(target_url, request)


@router.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_auth(path: str, request: Request) -> Response:
    target_url = _build_auth_target(path)
    return await _proxy_request(target_url, request)


@router.api_route(
    "/compras/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_compras(path: str, request: Request) -> Response:
    target_url = f"{settings.ms_compras_url}/{path}"
    return await _proxy_request(target_url, request)


@router.api_route(
    "/ventas/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_ventas(path: str, request: Request) -> Response:
    target_url = f"{settings.ms_ventas_url}/{path}"
    return await _proxy_request(target_url, request)


@router.api_route(
    "/finanzas/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_finanzas(path: str, request: Request) -> Response:
    target_url = f"{settings.ms_finanzas_url}/{path}"
    return await _proxy_request(target_url, request)


@router.api_route(
    "/reportes/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_reportes(path: str, request: Request) -> Response:
    target_url = f"{settings.ms_reportes_url}/{path}"
    return await _proxy_request(target_url, request)
