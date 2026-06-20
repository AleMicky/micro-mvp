import httpx
from fastapi import HTTPException, status

from app.core.config import settings

_TIMEOUT = 5.0


class CompanyClient:
    async def obtener_sucursal_por_id(self, sucursal_id: int) -> dict:
        """Obtiene sucursal y snapshot de compañía desde ms-company."""
        url = f"{settings.ms_company_url}/sucursales/{sucursal_id}"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo contactar ms-company: {exc}",
            ) from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sucursal {sucursal_id} no encontrada en ms-company",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al consultar sucursal en ms-company: {response.status_code}",
            )

        try:
            sucursal = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-company al consultar sucursal",
            ) from exc

        if not isinstance(sucursal, dict) or "id" not in sucursal:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-company al consultar sucursal",
            )

        compania_id = sucursal.get("compania_id")
        compania_nombre = await self._obtener_compania_nombre(client=None, compania_id=compania_id)

        return {
            "sucursal_id": sucursal["id"],
            "sucursal_codigo": sucursal.get("codigo"),
            "sucursal_nombre": sucursal.get("nombre"),
            "compania_id": compania_id,
            "compania_nombre": compania_nombre,
        }

    async def _obtener_compania_nombre(
        self,
        *,
        client: httpx.AsyncClient | None,
        compania_id: int | None,
    ) -> str | None:
        if compania_id is None:
            return None

        url = f"{settings.ms_company_url}/companias/{compania_id}"
        try:
            if client is not None:
                response = await client.get(url)
            else:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as own_client:
                    response = await own_client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo contactar ms-company: {exc}",
            ) from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al consultar compañía en ms-company: {response.status_code}",
            )

        try:
            compania = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-company al consultar compañía",
            ) from exc

        if not isinstance(compania, dict):
            return None
        return compania.get("nombre")

    async def listar_sucursales(self) -> list[dict]:
        """Lista sucursales desde ms-company (uso interno, p.ej. seed)."""
        url = f"{settings.ms_company_url}/sucursales"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(url, params={"limit": 500})
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

        try:
            sucursales = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-company al listar sucursales",
            ) from exc

        if not isinstance(sucursales, list):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-company al listar sucursales",
            )
        return sucursales

    async def listar_companias(self) -> list[dict]:
        """Lista compañías desde ms-company (uso interno, p.ej. seed)."""
        url = f"{settings.ms_company_url}/companias"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(url, params={"limit": 500})
        except httpx.RequestError as exc:
            raise RuntimeError(f"No se pudo contactar ms-company: {exc}") from exc

        if response.status_code >= 400:
            raise RuntimeError(f"Error al listar compañías: {response.status_code}")

        companias = response.json()
        if not isinstance(companias, list):
            raise RuntimeError("Respuesta inválida de ms-company al listar compañías")
        return companias

    async def obtener_snapshot_por_codigo_sucursal(self, sucursal_codigo: str) -> dict | None:
        """Resuelve snapshot de sucursal por código (uso interno, p.ej. seed)."""
        sucursales = await self.listar_sucursales()
        sucursal = next((s for s in sucursales if s.get("codigo") == sucursal_codigo), None)
        if not sucursal:
            return None

        companias = await self.listar_companias()
        compania = next((c for c in companias if c.get("id") == sucursal.get("compania_id")), None)

        return {
            "sucursal_id": sucursal["id"],
            "sucursal_codigo": sucursal.get("codigo"),
            "sucursal_nombre": sucursal.get("nombre"),
            "compania_id": sucursal.get("compania_id"),
            "compania_nombre": compania.get("nombre") if compania else None,
        }


company_client = CompanyClient()
