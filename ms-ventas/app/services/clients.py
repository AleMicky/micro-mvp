import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class InventarioClient:
    async def registrar_salida(self, *, producto_id: int, almacen_id: int, cantidad: float, observaciones: str | None = None) -> None:
        url = f"{settings.ms_inventario_url}/stock/salida"
        payload = {"producto_id": producto_id, "almacen_id": almacen_id, "cantidad": str(cantidad), "observaciones": observaciones}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Error inventario salida: {response.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Inventario no disponible: {exc}") from exc


class FinanzasClient:
    async def crear_cuenta_por_cobrar(self, *, referencia_tipo: str, referencia_id: int, cliente_id: int, monto: float, descripcion: str | None = None) -> None:
        url = f"{settings.ms_finanzas_url}/cuentas-por-cobrar"
        payload = {"referencia_tipo": referencia_tipo, "referencia_id": referencia_id, "tercero_id": cliente_id, "tercero_tipo": "CLIENTE", "monto": str(monto), "descripcion": descripcion}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Error finanzas CXC: {response.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Finanzas no disponible: {exc}") from exc


inventario_client = InventarioClient()
finanzas_client = FinanzasClient()
