import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class VentasClient:
    async def crear_venta(self, payload: dict) -> dict:
        url = f"{settings.ms_ventas_url}/ventas"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo contactar ms-ventas: {exc}",
            ) from exc
        if response.status_code >= 400:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except ValueError:
                pass
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
        return response.json()


ventas_client = VentasClient()
