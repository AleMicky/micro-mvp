from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.reportes import reporte_service

router = APIRouter(tags=["reportes"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ms-reportes"}


@router.get("/productos")
async def reporte_productos(db: AsyncSession = Depends(get_db)):
    return await reporte_service.reporte_productos(db)


@router.get("/stock")
async def reporte_stock(db: AsyncSession = Depends(get_db)):
    return await reporte_service.reporte_stock(db)


@router.get("/kardex/producto/{producto_id}")
async def reporte_kardex(producto_id: int, db: AsyncSession = Depends(get_db)):
    return await reporte_service.reporte_kardex(db, producto_id)


@router.get("/compras")
async def reporte_compras(db: AsyncSession = Depends(get_db)):
    return await reporte_service.reporte_compras(db)


@router.get("/ventas")
async def reporte_ventas(db: AsyncSession = Depends(get_db)):
    return await reporte_service.reporte_ventas(db)


@router.get("/finanzas")
async def reporte_finanzas(db: AsyncSession = Depends(get_db)):
    return await reporte_service.reporte_finanzas(db)


@router.get("/exportar/excel")
async def exportar_excel(tipo: str = Query("stock"), db: AsyncSession = Depends(get_db)):
    content, filename = await reporte_service.exportar_excel(db, tipo)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/exportar/pdf")
async def exportar_pdf(tipo: str = Query("stock"), db: AsyncSession = Depends(get_db)):
    content, filename = await reporte_service.exportar_pdf(db, tipo)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
