import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class CompanyClient:
    async def listar_sucursales(self) -> list[dict]:
        url = f"{settings.ms_company_url}/sucursales"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo contactar ms-company: {exc}",
            ) from exc
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al listar sucursales en ms-company: {response.status_code}",
            )
        return response.json()


company_client = CompanyClient()
