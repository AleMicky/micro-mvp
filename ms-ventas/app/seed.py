import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.models import Cliente, Factura, FacturaDetalle, Venta, VentaDetalle

logger = logging.getLogger(__name__)

CLIENTES = [
    {"codigo": "CLI-001", "nombre": "Comercial Azteca", "rfc": "CAZ900101ABC", "email": "compras@azteca.com"},
    {"codigo": "CLI-002", "nombre": "Tienda Express", "rfc": "TEX880202XYZ", "email": "pedidos@express.com"},
    {"codigo": "CLI-003", "nombre": "Corporativo Sur", "rfc": "CSU770303GHI", "email": "ventas@surnorte.com"},
]


async def run_seed() -> None:
    async with async_session() as db:
        clientes: dict[str, Cliente] = {}
        for data in CLIENTES:
            stmt = select(Cliente).where(Cliente.codigo == data["codigo"])
            c = (await db.execute(stmt)).scalar_one_or_none()
            if not c:
                c = Cliente(**data)
                db.add(c)
                await db.flush()
            clientes[data["codigo"]] = c
        await db.commit()

        if not (await db.execute(select(Venta).where(Venta.codigo == "VTA-00001"))).scalar_one_or_none():
            c1 = clientes["CLI-001"]
            v1 = Venta(codigo="VTA-00001", cliente_id=c1.id, almacen_id=1, estado="CONFIRMADA", fecha="2026-06-01", total=Decimal("1200.00"))
            db.add(v1)
            await db.flush()
            db.add(VentaDetalle(venta_id=v1.id, producto_id=1, cantidad=Decimal("6"), precio_unitario=Decimal("200"), subtotal=Decimal("1200")))

            c2 = clientes["CLI-002"]
            v2 = Venta(codigo="VTA-00002", cliente_id=c2.id, almacen_id=1, estado="CONFIRMADA", fecha="2026-06-05", total=Decimal("800.00"))
            db.add(v2)
            await db.flush()
            db.add(VentaDetalle(venta_id=v2.id, producto_id=2, cantidad=Decimal("4"), precio_unitario=Decimal("200"), subtotal=Decimal("800")))
            await db.commit()

        if not (await db.execute(select(Factura).where(Factura.codigo == "FAC-00001"))).scalar_one_or_none():
            v1 = (await db.execute(select(Venta).where(Venta.codigo == "VTA-00001"))).scalar_one()
            f1 = Factura(codigo="FAC-00001", venta_id=v1.id, estado="FACTURADA", fecha="2026-06-02", subtotal=Decimal("1200"), impuesto=Decimal("0"), total=Decimal("1200"))
            db.add(f1)
            await db.flush()
            db.add(FacturaDetalle(factura_id=f1.id, producto_id=1, cantidad=Decimal("6"), precio_unitario=Decimal("200"), subtotal=Decimal("1200")))

            v2 = (await db.execute(select(Venta).where(Venta.codigo == "VTA-00002"))).scalar_one()
            f2 = Factura(codigo="FAC-00002", venta_id=v2.id, estado="FACTURADA", fecha="2026-06-06", subtotal=Decimal("800"), impuesto=Decimal("0"), total=Decimal("800"))
            db.add(f2)
            await db.flush()
            db.add(FacturaDetalle(factura_id=f2.id, producto_id=2, cantidad=Decimal("4"), precio_unitario=Decimal("200"), subtotal=Decimal("800")))
            await db.commit()

    logger.info("Seed ms-ventas completado")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())
