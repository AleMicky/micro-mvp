import httpx
from fastapi import HTTPException, status

from app.core.config import settings

_TIMEOUT = 15.0


class CatalogosClient:
    async def obtener_producto_por_id(self, producto_id: int) -> dict:
        url = f"{settings.ms_catalogos_url}/productos/{producto_id}"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ms-catalogos no disponible: {exc}",
            ) from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Producto {producto_id} no encontrado en catálogos",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al consultar producto en catálogos: {response.text}",
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-catalogos",
            ) from exc

        if not data.get("id"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-catalogos",
            )
        return data


catalogos_client = CatalogosClient()
