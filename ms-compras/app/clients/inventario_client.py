from decimal import Decimal

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

_TIMEOUT = 15.0


class InventarioClient:
    async def obtener_almacen_por_id(self, almacen_id: int) -> dict:
        url = f"{settings.ms_inventario_url}/almacenes/{almacen_id}"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ms-inventario no disponible: {exc}",
            ) from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Almacén {almacen_id} no encontrado en inventario",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al consultar almacén en inventario: {response.text}",
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-inventario",
            ) from exc

        if not data.get("id"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de ms-inventario",
            )
        return data

    async def registrar_ingreso_stock(self, payload: dict) -> None:
        url = f"{settings.ms_inventario_url}/stock/ingreso"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Error al registrar ingreso en inventario: {response.text}",
                    )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ms-inventario no disponible: {exc}",
            ) from exc

    async def registrar_ingreso(
        self,
        *,
        producto_id: int,
        almacen_id: int,
        cantidad: Decimal,
        costo_unitario: Decimal | None = None,
        observacion: str | None = None,
        referencia_tipo: str | None = None,
        referencia_id: int | None = None,
        creado_por: str = "sistema",
    ) -> None:
        payload: dict = {
            "producto_id": producto_id,
            "almacen_id": almacen_id,
            "cantidad": str(cantidad),
            "observaciones": observacion,
            "referencia_tipo": referencia_tipo,
            "referencia_id": referencia_id,
            "creado_por": creado_por,
        }
        if costo_unitario is not None:
            payload["costo_unitario"] = str(costo_unitario)
        await self.registrar_ingreso_stock(payload)


inventario_client = InventarioClient()
