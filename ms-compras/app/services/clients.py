from decimal import Decimal

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class InventarioClient:
    async def registrar_ingreso(
        self,
        *,
        producto_id: int,
        almacen_id: int,
        cantidad: Decimal,
        observacion: str | None = None,
        referencia_tipo: str | None = None,
        referencia_id: int | None = None,
        creado_por: str = "sistema",
    ) -> None:
        url = f"{settings.ms_inventario_url}/stock/ingreso"
        payload = {
            "producto_id": producto_id,
            "almacen_id": almacen_id,
            "cantidad": str(cantidad),
            "observaciones": observacion,
            "referencia_tipo": referencia_tipo,
            "referencia_id": referencia_id,
            "creado_por": creado_por,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Error al registrar ingreso en inventario: {response.text}",
                    )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Inventario no disponible: {exc}",
            ) from exc


inventario_client = InventarioClient()
