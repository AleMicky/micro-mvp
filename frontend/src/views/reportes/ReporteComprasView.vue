<script setup lang="ts">
import ReporteGenericView, { type ReportSummaryCell, type ReportTotalCell } from './ReporteGenericView.vue'
import { comprasService } from '@/services/compras.service'
import { reportesService } from '@/services/reportes.service'
import { formatDateCompact, formatMoney } from '@/utils/format'
import { ESTADO_COMPRA_COLORS, type OrdenCompra } from '@/types/compras.types'

const headers = [
  { title: 'Número', key: 'codigo', width: 108 },
  { title: 'Proveedor', key: 'proveedor_nombre' },
  { title: 'Fecha', key: 'fecha', width: 120 },
  { title: 'Estado', key: 'estado', width: 108, sortable: false },
  { title: 'Ítems', key: 'items_count', align: 'end' as const, width: 64, sortable: false },
  { title: 'Total', key: 'total', align: 'end' as const, width: 108 },
]

async function prepare(items: unknown[]) {
  const { data: proveedores } = await comprasService.getProveedores()
  const proveedorMap = Object.fromEntries(proveedores.map((p) => [p.id, p.nombre]))

  return (items as OrdenCompra[]).map((o) => ({
    ...o,
    proveedor_nombre: proveedorMap[o.proveedor_id] ?? `Proveedor ${o.proveedor_id}`,
    items_count: o.detalles?.length ?? 0,
  }))
}

function summary(rows: Record<string, unknown>[]): ReportSummaryCell[] {
  const aprobadas = rows.filter((r) => r.estado === 'APROBADA').length
  const borradores = rows.filter((r) => r.estado === 'BORRADOR').length
  const montoTotal = rows.reduce((sum, r) => sum + Number(r.total), 0)
  const montoAprobado = rows
    .filter((r) => r.estado === 'APROBADA')
    .reduce((sum, r) => sum + Number(r.total), 0)

  return [
    { label: 'Órdenes', value: String(rows.length), meta: 'Total registradas' },
    { label: 'Aprobadas', value: String(aprobadas), meta: formatMoney(montoAprobado), variant: 'accent' },
    { label: 'Borradores', value: String(borradores), meta: 'Pendientes de aprobación' },
    { label: 'Monto total', value: formatMoney(montoTotal), valueSm: true, meta: 'Todas las órdenes' },
  ]
}

function totals(rows: Record<string, unknown>[]): ReportTotalCell[] {
  const monto = rows.reduce((sum, r) => sum + Number(r.total), 0)
  const items = rows.reduce((sum, r) => sum + Number(r.items_count), 0)
  return [
    { label: 'Órdenes', value: String(rows.length) },
    { label: 'Ítems', value: String(items) },
    { label: 'Σ total', value: formatMoney(monto), accent: true },
  ]
}
</script>

<template>
  <ReporteGenericView
    tipo="compras"
    title="Reporte de compras"
    subtitle="Órdenes de compra registradas"
    icon="mdi-cart-arrow-down"
    :loader="reportesService.getCompras"
    :headers="headers"
    :prepare="prepare"
    :summary="summary"
    :totals="totals"
    table-title="Órdenes de compra"
    table-subtitle="Listado completo de órdenes"
    search-label="Buscar orden o proveedor..."
    empty-subtitle="No hay órdenes de compra registradas."
  >
    <template #item.codigo="{ value }">
      <span class="font-weight-medium">{{ value }}</span>
    </template>

    <template #item.proveedor_nombre="{ value }">
      <span class="cell-ellipsis" :title="String(value ?? '')">{{ value }}</span>
    </template>

    <template #item.fecha="{ value }">
      <span class="text-caption text-medium-emphasis">
        {{ value ? formatDateCompact(String(value)) : '—' }}
      </span>
    </template>

    <template #item.estado="{ value }">
      <v-chip
        :color="ESTADO_COMPRA_COLORS[String(value)] ?? 'default'"
        size="x-small"
        variant="tonal"
        label
      >
        {{ value }}
      </v-chip>
    </template>

    <template #item.items_count="{ value }">
      <span class="text-medium-emphasis">{{ value }}</span>
    </template>

    <template #item.total="{ value }">
      <span class="font-weight-medium">{{ formatMoney(value) }}</span>
    </template>
  </ReporteGenericView>
</template>
