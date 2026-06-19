import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class InventarioClient:
    async def obtener_stock(self, producto_id: int) -> dict:
        url = f"{settings.ms_inventario_url}/stock/consolidado/producto/{producto_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo contactar ms-inventario: {exc}",
            ) from exc
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al consultar stock en ms-inventario: {response.status_code}",
            )
        return response.json()

    async def listar_almacenes(self) -> list[dict]:
        url = f"{settings.ms_inventario_url}/almacenes"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params={"solo_activos": "true"})
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo contactar ms-inventario: {exc}",
            ) from exc
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al listar almacenes en ms-inventario: {response.status_code}",
            )
        return response.json()

    async def listar_existencias_por_almacen(self, almacen_id: int) -> list[dict]:
        url = f"{settings.ms_inventario_url}/existencias/almacen/{almacen_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params={"limit": 500})
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo contactar ms-inventario: {exc}",
            ) from exc
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al listar existencias en ms-inventario: {response.status_code}",
            )
        return response.json()


inventario_client = InventarioClient()
