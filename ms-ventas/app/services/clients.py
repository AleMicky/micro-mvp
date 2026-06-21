import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class CatalogosClient:
    async def obtener_producto(self, producto_id: int) -> dict:
        url = f"{settings.ms_catalogos_url}/productos/{producto_id}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Producto {producto_id} no encontrado")
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Error catálogos: {response.text}")
                return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Catálogos no disponible: {exc}") from exc

    async def verificar_stock(self, producto_id: int, almacen_id: int, cantidad: float) -> None:
        url = f"{settings.ms_inventario_url}/existencias/producto/{producto_id}/almacen/{almacen_id}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=400,
                        detail=f"El producto {producto_id} no tiene existencia registrada en este almacén",
                    )
                data = response.json()
                disponible = float(data.get("cantidad_actual", 0))
                if disponible < cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente producto {producto_id}. Disponible: {disponible}, solicitado: {cantidad}",
                    )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Inventario no disponible: {exc}") from exc


class InventarioClient:
    async def registrar_salida(self, *, producto_id: int, almacen_id: int, cantidad: float, observaciones: str | None = None) -> None:
        url = f"{settings.ms_inventario_url}/stock/salida"
        payload = {
            "producto_id": producto_id,
            "almacen_id": almacen_id,
            "cantidad": str(cantidad),
            "observaciones": observaciones,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Error inventario salida: {response.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Inventario no disponible: {exc}") from exc


class FinanzasClient:
    async def crear_cuenta_por_cobrar(
        self, *, referencia_tipo: str, referencia_id: int, cliente_id: int, monto: float, descripcion: str | None = None
    ) -> None:
        url = f"{settings.ms_finanzas_url}/cuentas-por-cobrar"
        payload = {
            "referencia_tipo": referencia_tipo,
            "referencia_id": referencia_id,
            "tercero_id": cliente_id,
            "tercero_tipo": "CLIENTE",
            "monto": str(monto),
            "descripcion": descripcion,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Error finanzas CXC: {response.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Finanzas no disponible: {exc}") from exc


class ClientesClient:
    async def validar_cliente(self, cliente_id: int) -> dict:
        url = f"{settings.ms_clientes_url}/clientes/{cliente_id}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Error clientes: {response.text}")
                return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Clientes no disponible: {exc}") from exc

    async def asignar_puntos(self, cliente_id: int, puntos: int, referencia: str) -> None:
        url = f"{settings.ms_clientes_url}/clientes/{cliente_id}/puntos"
        payload = {"puntos": puntos, "motivo": "Puntos por compra", "referencia": referencia}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Error asignando puntos: {response.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Clientes no disponible: {exc}") from exc


catalogos_client = CatalogosClient()
inventario_client = InventarioClient()
finanzas_client = FinanzasClient()
clientes_client = ClientesClient()
