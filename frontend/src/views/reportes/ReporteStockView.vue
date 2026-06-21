<script setup lang="ts">
import ReporteGenericView, { type ReportSummaryCell, type ReportTotalCell } from './ReporteGenericView.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { reportesService } from '@/services/reportes.service'
import { formatInteger } from '@/utils/format'
import type { Existencia } from '@/types/inventario.types'

const headers = [
  { title: 'Producto', key: 'producto_nombre' },
  { title: 'Código', key: 'producto_codigo', width: 100 },
  { title: 'Almacén', key: 'almacen_nombre', width: 140 },
  { title: 'Cant.', key: 'cantidad_actual', align: 'end' as const, width: 72 },
  { title: 'Mín.', key: 'stock_minimo', align: 'end' as const, width: 64 },
  { title: 'Máx.', key: 'stock_maximo', align: 'end' as const, width: 64 },
  { title: 'Estado', key: 'stock_status', width: 96, sortable: false },
]

function getStockStatus(item: Record<string, unknown>): 'bajo' | 'ok' {
  const actual = Number(item.cantidad_actual)
  const minimo = Number(item.stock_minimo)
  if (minimo > 0 && actual <= minimo) return 'bajo'
  return 'ok'
}

async function prepare(items: unknown[]) {
  const [productosRes, almacenesRes] = await Promise.all([
    catalogosService.getProductos(),
    inventarioService.getAlmacenes(),
  ])
  const productoMap = Object.fromEntries(productosRes.data.map((p) => [p.id, p]))
  const almacenMap = Object.fromEntries(almacenesRes.data.map((a) => [a.id, a.nombre]))

  return (items as Existencia[]).map((e) => {
    const producto = productoMap[e.producto_id]
    return {
      ...e,
      producto_nombre: producto?.nombre ?? `Producto ${e.producto_id}`,
      producto_codigo: producto?.codigo ?? '',
      almacen_nombre: almacenMap[e.almacen_id] ?? `Almacén ${e.almacen_id}`,
      stock_status: getStockStatus(e as unknown as Record<string, unknown>),
    }
  })
}

function summary(rows: Record<string, unknown>[]): ReportSummaryCell[] {
  const bajo = rows.filter((r) => getStockStatus(r) === 'bajo').length
  const total = Math.trunc(rows.reduce((sum, r) => sum + Number(r.cantidad_actual), 0))
  const almacenes = new Set(rows.map((r) => r.almacen_id)).size
  const productos = new Set(rows.map((r) => r.producto_id)).size

  return [
    { label: 'Registros', value: String(rows.length), meta: 'Existencias activas' },
    { label: 'Unidades', value: formatInteger(total), meta: `${productos} producto(s)` },
    { label: 'Almacenes', value: String(almacenes), meta: 'Con stock registrado' },
    { label: 'Stock bajo', value: String(bajo), meta: bajo ? 'Requiere atención' : 'Todo en rango', variant: bajo ? 'accent' : undefined },
  ]
}

function totals(rows: Record<string, unknown>[]): ReportTotalCell[] {
  const bajo = rows.filter((r) => getStockStatus(r) === 'bajo').length
  const total = Math.trunc(rows.reduce((sum, r) => sum + Number(r.cantidad_actual), 0))
  return [
    { label: 'Filas', value: String(rows.length) },
    { label: 'Unidades', value: formatInteger(total) },
    { label: 'Stock bajo', value: String(bajo), colorClass: bajo ? 'text-warning' : '' },
  ]
}
</script>

<template>
  <ReporteGenericView
    tipo="stock"
    title="Reporte de stock"
    subtitle="Existencias por producto y almacén"
    icon="mdi-package-variant-closed"
    :loader="reportesService.getStock"
    :headers="headers"
    :prepare="prepare"
    :summary="summary"
    :totals="totals"
    table-title="Existencias"
    table-subtitle="Stock actual en todos los almacenes"
    search-label="Buscar producto o almacén..."
    empty-subtitle="No hay existencias registradas en el inventario."
  >
    <template #item.producto_nombre="{ value }">
      <span class="cell-ellipsis cell-ellipsis--wide" :title="String(value ?? '')">{{ value }}</span>
    </template>

    <template #item.almacen_nombre="{ value }">
      <span class="cell-ellipsis" :title="String(value ?? '')">{{ value }}</span>
    </template>

    <template #item.cantidad_actual="{ value }">
      <span class="font-weight-medium">{{ formatInteger(value) }}</span>
    </template>

    <template #item.stock_minimo="{ value }">
      <span class="text-medium-emphasis">{{ formatInteger(value) }}</span>
    </template>

    <template #item.stock_maximo="{ value }">
      <span class="text-medium-emphasis">{{ formatInteger(value) }}</span>
    </template>

    <template #item.stock_status="{ item }">
      <v-chip
        :color="getStockStatus(item) === 'bajo' ? 'warning' : 'success'"
        size="x-small"
        variant="tonal"
        label
      >
        {{ getStockStatus(item) === 'bajo' ? 'Bajo' : 'OK' }}
      </v-chip>
    </template>
  </ReporteGenericView>
</template>

<style scoped>
.cell-ellipsis--wide {
  max-width: 180px;
}
</style>
