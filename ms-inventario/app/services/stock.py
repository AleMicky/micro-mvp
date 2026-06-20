from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.almacen import crud_almacen
from app.crud.existencia import crud_existencia
from app.enums.tipo_movimiento import ReferenciaTipo, TipoMovimiento
from app.models.ajuste_detalle import AjusteDetalle
from app.models.ajuste_inventario import AjusteInventario
from app.models.existencia import Existencia
from app.models.movimiento_inventario import MovimientoInventario
from app.models.transferencia_detalle import TransferenciaDetalle
from app.models.transferencia_inventario import TransferenciaInventario
from app.schemas.operacion import (
    AjusteInventarioResponse,
    StockOperacionResponse,
    TransferenciaInventarioResponse,
)
from app.schemas.stock import (
    StockAjusteRequest,
    StockIngresoRequest,
    StockSalidaRequest,
    StockTransferenciaRequest,
)
from app.services.catalogos import catalogos_client
from app.events.publisher import publish_event


class StockService:
    async def _validar_almacen(self, db: AsyncSession, almacen_id: int) -> None:
        almacen = await crud_almacen.get(db, almacen_id)
        if not almacen or not almacen.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Almacén {almacen_id} no encontrado o inactivo",
            )

    async def _registrar_movimiento(
        self,
        db: AsyncSession,
        *,
        tipo: TipoMovimiento,
        producto_id: int,
        almacen_id: int,
        cantidad: Decimal,
        cantidad_anterior: Decimal,
        cantidad_nueva: Decimal,
        referencia_tipo: ReferenciaTipo | None = None,
        referencia_id: int | None = None,
        observaciones: str | None = None,
    ) -> MovimientoInventario:
        movimiento = MovimientoInventario(
            tipo=tipo.value,
            producto_id=producto_id,
            almacen_id=almacen_id,
            cantidad=cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            referencia_tipo=referencia_tipo.value if referencia_tipo else None,
            referencia_id=referencia_id,
            observaciones=observaciones,
        )
        db.add(movimiento)
        await db.flush()
        return movimiento

    async def _obtener_o_crear_existencia(
        self,
        db: AsyncSession,
        *,
        producto_id: int,
        almacen_id: int,
        stock_minimo: Decimal | None = None,
        stock_maximo: Decimal | None = None,
    ) -> Existencia:
        existencia = await crud_existencia.get_by_producto_almacen(
            db, producto_id=producto_id, almacen_id=almacen_id
        )
        if existencia:
            return existencia

        return await crud_existencia.create(
            db,
            producto_id=producto_id,
            almacen_id=almacen_id,
            stock_minimo=stock_minimo or Decimal("0"),
            stock_maximo=stock_maximo,
        )

    async def ingreso(self, db: AsyncSession, payload: StockIngresoRequest) -> StockOperacionResponse:
        await catalogos_client.validar_producto(payload.producto_id)
        await self._validar_almacen(db, payload.almacen_id)

        existencia = await self._obtener_o_crear_existencia(
            db,
            producto_id=payload.producto_id,
            almacen_id=payload.almacen_id,
            stock_minimo=payload.stock_minimo,
            stock_maximo=payload.stock_maximo,
        )

        cantidad_anterior = existencia.cantidad_actual
        cantidad_nueva = cantidad_anterior + payload.cantidad
        existencia.cantidad_actual = cantidad_nueva

        if payload.stock_minimo is not None:
            existencia.stock_minimo = payload.stock_minimo
        if payload.stock_maximo is not None:
            existencia.stock_maximo = payload.stock_maximo

        referencia = ReferenciaTipo.INGRESO
        if payload.referencia_tipo:
            try:
                referencia = ReferenciaTipo(payload.referencia_tipo)
            except ValueError:
                referencia = ReferenciaTipo.INGRESO

        movimiento = await self._registrar_movimiento(
            db,
            tipo=TipoMovimiento.INGRESO,
            producto_id=payload.producto_id,
            almacen_id=payload.almacen_id,
            cantidad=payload.cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            referencia_tipo=referencia,
            referencia_id=payload.referencia_id,
            observaciones=payload.observaciones,
        )

        await db.commit()
        await db.refresh(existencia)
        await db.refresh(movimiento)

        await publish_event(
            "InventoryUpdated",
            {"producto_id": existencia.producto_id, "almacen_id": existencia.almacen_id, "cantidad": float(cantidad_nueva)},
        )
        if existencia.stock_minimo and cantidad_nueva <= existencia.stock_minimo:
            await publish_event(
                "StockLow",
                {"producto_id": existencia.producto_id, "almacen_id": existencia.almacen_id, "cantidad": float(cantidad_nueva)},
            )

        return StockOperacionResponse(
            existencia_id=existencia.id,
            producto_id=existencia.producto_id,
            almacen_id=existencia.almacen_id,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            movimiento=movimiento,
        )

    async def salida(self, db: AsyncSession, payload: StockSalidaRequest) -> StockOperacionResponse:
        await catalogos_client.validar_producto(payload.producto_id)
        await self._validar_almacen(db, payload.almacen_id)

        existencia = await crud_existencia.get_by_producto_almacen(
            db, producto_id=payload.producto_id, almacen_id=payload.almacen_id
        )
        if not existencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe existencia para el producto en el almacén indicado",
            )

        cantidad_anterior = existencia.cantidad_actual
        if cantidad_anterior < payload.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {cantidad_anterior}, solicitado: {payload.cantidad}",
            )

        cantidad_nueva = cantidad_anterior - payload.cantidad
        existencia.cantidad_actual = cantidad_nueva

        movimiento = await self._registrar_movimiento(
            db,
            tipo=TipoMovimiento.SALIDA,
            producto_id=payload.producto_id,
            almacen_id=payload.almacen_id,
            cantidad=payload.cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            referencia_tipo=ReferenciaTipo.SALIDA,
            observaciones=payload.observaciones,
        )

        await db.commit()
        await db.refresh(existencia)
        await db.refresh(movimiento)

        await publish_event(
            "InventoryUpdated",
            {"producto_id": existencia.producto_id, "almacen_id": existencia.almacen_id, "cantidad": float(cantidad_nueva)},
        )
        if existencia.stock_minimo and cantidad_nueva <= existencia.stock_minimo:
            await publish_event(
                "StockLow",
                {"producto_id": existencia.producto_id, "almacen_id": existencia.almacen_id, "cantidad": float(cantidad_nueva)},
            )

        return StockOperacionResponse(
            existencia_id=existencia.id,
            producto_id=existencia.producto_id,
            almacen_id=existencia.almacen_id,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            movimiento=movimiento,
        )

    async def ajuste(self, db: AsyncSession, payload: StockAjusteRequest) -> AjusteInventarioResponse:
        await self._validar_almacen(db, payload.almacen_id)

        ajuste = AjusteInventario(
            almacen_id=payload.almacen_id,
            motivo=payload.motivo,
            observaciones=payload.observaciones,
        )
        db.add(ajuste)
        await db.flush()

        movimientos: list[MovimientoInventario] = []
        detalles_creados: list[AjusteDetalle] = []

        for detalle in payload.detalles:
            await catalogos_client.validar_producto(detalle.producto_id)

            existencia = await self._obtener_o_crear_existencia(
                db,
                producto_id=detalle.producto_id,
                almacen_id=payload.almacen_id,
            )

            cantidad_anterior = existencia.cantidad_actual
            cantidad_nueva = detalle.cantidad_nueva
            diferencia = cantidad_nueva - cantidad_anterior

            if diferencia == 0:
                continue

            if diferencia < 0 and cantidad_anterior < abs(diferencia):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Stock insuficiente para ajuste negativo del producto {detalle.producto_id}. "
                        f"Disponible: {cantidad_anterior}, solicitado: {cantidad_nueva}"
                    ),
                )

            existencia.cantidad_actual = cantidad_nueva

            tipo = (
                TipoMovimiento.AJUSTE_POSITIVO
                if diferencia > 0
                else TipoMovimiento.AJUSTE_NEGATIVO
            )

            detalle_ajuste = AjusteDetalle(
                ajuste_id=ajuste.id,
                producto_id=detalle.producto_id,
                cantidad_anterior=cantidad_anterior,
                cantidad_nueva=cantidad_nueva,
                diferencia=diferencia,
            )
            db.add(detalle_ajuste)
            detalles_creados.append(detalle_ajuste)

            movimiento = await self._registrar_movimiento(
                db,
                tipo=tipo,
                producto_id=detalle.producto_id,
                almacen_id=payload.almacen_id,
                cantidad=abs(diferencia),
                cantidad_anterior=cantidad_anterior,
                cantidad_nueva=cantidad_nueva,
                referencia_tipo=ReferenciaTipo.AJUSTE,
                referencia_id=ajuste.id,
                observaciones=payload.observaciones,
            )
            movimientos.append(movimiento)

        if not movimientos:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ajuste no generó cambios en el inventario",
            )

        await db.commit()
        await db.refresh(ajuste)
        for detalle_ajuste in detalles_creados:
            await db.refresh(detalle_ajuste)
        for movimiento in movimientos:
            await db.refresh(movimiento)

        return AjusteInventarioResponse(
            id=ajuste.id,
            codigo=ajuste.codigo,
            almacen_id=ajuste.almacen_id,
            motivo=ajuste.motivo,
            observaciones=ajuste.observaciones,
            activo=ajuste.activo,
            creado_en=ajuste.creado_en,
            actualizado_en=ajuste.actualizado_en,
            detalles=detalles_creados,
            movimientos=movimientos,
        )

    async def transferencia(
        self,
        db: AsyncSession,
        payload: StockTransferenciaRequest,
    ) -> TransferenciaInventarioResponse:
        if payload.almacen_origen_id == payload.almacen_destino_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El almacén origen y destino deben ser diferentes",
            )

        await self._validar_almacen(db, payload.almacen_origen_id)
        await self._validar_almacen(db, payload.almacen_destino_id)

        transferencia = TransferenciaInventario(
            almacen_origen_id=payload.almacen_origen_id,
            almacen_destino_id=payload.almacen_destino_id,
            observaciones=payload.observaciones,
        )
        db.add(transferencia)
        await db.flush()

        movimientos: list[MovimientoInventario] = []
        detalles_creados: list[TransferenciaDetalle] = []

        for detalle in payload.detalles:
            await catalogos_client.validar_producto(detalle.producto_id)

            existencia_origen = await crud_existencia.get_by_producto_almacen(
                db,
                producto_id=detalle.producto_id,
                almacen_id=payload.almacen_origen_id,
            )
            if not existencia_origen:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"No existe stock del producto {detalle.producto_id} "
                        f"en el almacén origen {payload.almacen_origen_id}"
                    ),
                )

            cantidad_anterior_origen = existencia_origen.cantidad_actual
            if cantidad_anterior_origen < detalle.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Stock insuficiente en origen para producto {detalle.producto_id}. "
                        f"Disponible: {cantidad_anterior_origen}, solicitado: {detalle.cantidad}"
                    ),
                )

            cantidad_nueva_origen = cantidad_anterior_origen - detalle.cantidad
            existencia_origen.cantidad_actual = cantidad_nueva_origen

            existencia_destino = await self._obtener_o_crear_existencia(
                db,
                producto_id=detalle.producto_id,
                almacen_id=payload.almacen_destino_id,
            )
            cantidad_anterior_destino = existencia_destino.cantidad_actual
            cantidad_nueva_destino = cantidad_anterior_destino + detalle.cantidad
            existencia_destino.cantidad_actual = cantidad_nueva_destino

            detalle_transferencia = TransferenciaDetalle(
                transferencia_id=transferencia.id,
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad,
            )
            db.add(detalle_transferencia)
            detalles_creados.append(detalle_transferencia)

            movimiento_salida = await self._registrar_movimiento(
                db,
                tipo=TipoMovimiento.TRANSFERENCIA_SALIDA,
                producto_id=detalle.producto_id,
                almacen_id=payload.almacen_origen_id,
                cantidad=detalle.cantidad,
                cantidad_anterior=cantidad_anterior_origen,
                cantidad_nueva=cantidad_nueva_origen,
                referencia_tipo=ReferenciaTipo.TRANSFERENCIA,
                referencia_id=transferencia.id,
                observaciones=payload.observaciones,
            )
            movimiento_entrada = await self._registrar_movimiento(
                db,
                tipo=TipoMovimiento.TRANSFERENCIA_ENTRADA,
                producto_id=detalle.producto_id,
                almacen_id=payload.almacen_destino_id,
                cantidad=detalle.cantidad,
                cantidad_anterior=cantidad_anterior_destino,
                cantidad_nueva=cantidad_nueva_destino,
                referencia_tipo=ReferenciaTipo.TRANSFERENCIA,
                referencia_id=transferencia.id,
                observaciones=payload.observaciones,
            )
            movimientos.extend([movimiento_salida, movimiento_entrada])

        await db.commit()
        await db.refresh(transferencia)
        for detalle_transferencia in detalles_creados:
            await db.refresh(detalle_transferencia)
        for movimiento in movimientos:
            await db.refresh(movimiento)

        for detalle in payload.detalles:
            await publish_event(
                "TransferCompleted",
                {
                    "transferencia_id": transferencia.id,
                    "producto_id": detalle.producto_id,
                    "cantidad": float(detalle.cantidad),
                    "origen": payload.almacen_origen_id,
                    "destino": payload.almacen_destino_id,
                },
            )

        return TransferenciaInventarioResponse(
            id=transferencia.id,
            codigo=transferencia.codigo,
            almacen_origen_id=transferencia.almacen_origen_id,
            almacen_destino_id=transferencia.almacen_destino_id,
            estado=transferencia.estado,
            observaciones=transferencia.observaciones,
            activo=transferencia.activo,
            creado_en=transferencia.creado_en,
            actualizado_en=transferencia.actualizado_en,
            detalles=detalles_creados,
            movimientos=movimientos,
        )


stock_service = StockService()
