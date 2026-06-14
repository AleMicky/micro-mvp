import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class CatalogosClient:
    async def validar_producto(self, producto_id: int) -> None:
        url = f"{settings.ms_catalogos_url}/productos/{producto_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo contactar ms-catalogos: {exc}",
            ) from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {producto_id} no encontrado en ms-catalogos",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al validar producto en ms-catalogos: {response.status_code}",
            )


catalogos_client = CatalogosClient()
