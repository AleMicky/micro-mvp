import csv
import io
import json
from typing import Any

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Exportacion, ReporteGenerado


class ReporteService:
    async def _fetch(self, url: str) -> Any:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(url)
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Error al consultar {url}: {response.text}")
                return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Servicio no disponible: {url}") from exc

    async def _registrar(self, db: AsyncSession, tipo: str, parametros: dict | None = None) -> None:
        db.add(ReporteGenerado(tipo=tipo, parametros=json.dumps(parametros or {})))
        await db.commit()

    async def reporte_productos(self, db: AsyncSession) -> dict:
        data = await self._fetch(f"{settings.ms_catalogos_url}/productos")
        await self._registrar(db, "productos")
        return {"tipo": "productos", "total": len(data), "items": data}

    async def reporte_stock(self, db: AsyncSession) -> dict:
        data = await self._fetch(f"{settings.ms_inventario_url}/existencias")
        await self._registrar(db, "stock")
        return {"tipo": "stock", "total": len(data), "items": data}

    async def reporte_kardex(self, db: AsyncSession, producto_id: int) -> dict:
        data = await self._fetch(f"{settings.ms_inventario_url}/movimientos?producto_id={producto_id}")
        await self._registrar(db, "kardex", {"producto_id": producto_id})
        return {"tipo": "kardex", "producto_id": producto_id, "total": len(data), "items": data}

    async def reporte_compras(self, db: AsyncSession) -> dict:
        data = await self._fetch(f"{settings.ms_compras_url}/ordenes")
        await self._registrar(db, "compras")
        return {"tipo": "compras", "total": len(data), "items": data}

    async def reporte_ventas(self, db: AsyncSession) -> dict:
        data = await self._fetch(f"{settings.ms_ventas_url}/ventas")
        await self._registrar(db, "ventas")
        return {"tipo": "ventas", "total": len(data), "items": data}

    async def reporte_finanzas(self, db: AsyncSession) -> dict:
        cxc = await self._fetch(f"{settings.ms_finanzas_url}/cuentas-por-cobrar")
        cxp = await self._fetch(f"{settings.ms_finanzas_url}/cuentas-por-pagar")
        await self._registrar(db, "finanzas")
        return {
            "tipo": "finanzas",
            "cuentas_por_cobrar": cxc,
            "cuentas_por_pagar": cxp,
            "total_cxc": len(cxc),
            "total_cxp": len(cxp),
        }

    async def exportar_excel(self, db: AsyncSession, tipo: str = "stock") -> tuple[bytes, str]:
        reporte = await getattr(self, f"reporte_{tipo}")(db)
        items = reporte.get("items", reporte.get("cuentas_por_cobrar", []))
        output = io.StringIO()
        if items:
            writer = csv.DictWriter(output, fieldnames=items[0].keys())
            writer.writeheader()
            for row in items:
                writer.writerow({k: str(v) for k, v in row.items()})
        else:
            output.write("sin_datos\n")
        content = output.getvalue().encode("utf-8-sig")
        filename = f"reporte_{tipo}.csv"
        db.add(Exportacion(tipo_reporte=tipo, formato="excel", archivo=filename))
        await db.commit()
        return content, filename

    async def exportar_pdf(self, db: AsyncSession, tipo: str = "stock") -> tuple[bytes, str]:
        reporte = await getattr(self, f"reporte_{tipo}")(db)
        text = f"Reporte {tipo.upper()}\n\n{json.dumps(reporte, indent=2, default=str)}"
        content = text.encode("utf-8")
        filename = f"reporte_{tipo}.txt"
        db.add(Exportacion(tipo_reporte=tipo, formato="pdf", archivo=filename))
        await db.commit()
        return content, filename


reporte_service = ReporteService()
