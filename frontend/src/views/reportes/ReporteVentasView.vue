<script setup lang="ts">
import ReporteGenericView, { type ReportSummaryCell, type ReportTotalCell } from './ReporteGenericView.vue'
import { reportesService } from '@/services/reportes.service'
import { ventasService } from '@/services/ventas.service'
import { formatDateCompact, formatMoney } from '@/utils/format'
import { ESTADO_VENTA_COLORS, type Venta } from '@/types/ventas.types'

const headers = [
  { title: 'Número', key: 'codigo', width: 108 },
  { title: 'Cliente', key: 'cliente_nombre' },
  { title: 'Fecha', key: 'fecha', width: 120 },
  { title: 'Estado', key: 'estado', width: 108, sortable: false },
  { title: 'Ítems', key: 'items_count', align: 'end' as const, width: 64, sortable: false },
  { title: 'Total', key: 'total', align: 'end' as const, width: 108 },
]

async function prepare(items: unknown[]) {
  const { data: clientes } = await ventasService.getClientes()
  const clienteMap = Object.fromEntries(clientes.map((c) => [c.id, c.nombre]))

  return (items as Venta[]).map((v) => ({
    ...v,
    cliente_nombre: clienteMap[v.cliente_id] ?? `Cliente ${v.cliente_id}`,
    items_count: v.detalles?.length ?? 0,
  }))
}

function summary(rows: Record<string, unknown>[]): ReportSummaryCell[] {
  const confirmadas = rows.filter((r) => r.estado === 'CONFIRMADA' || r.estado === 'FACTURADA').length
  const montoTotal = rows.reduce((sum, r) => sum + Number(r.total), 0)
  const montoConfirmado = rows
    .filter((r) => r.estado === 'CONFIRMADA' || r.estado === 'FACTURADA')
    .reduce((sum, r) => sum + Number(r.total), 0)

  return [
    { label: 'Ventas', value: String(rows.length), meta: 'Total registradas' },
    { label: 'Confirmadas', value: String(confirmadas), meta: formatMoney(montoConfirmado), variant: 'accent' },
    { label: 'Monto total', value: formatMoney(montoTotal), valueSm: true, meta: 'Todas las ventas' },
    {
      label: 'Ticket prom.',
      value: rows.length ? formatMoney(montoTotal / rows.length) : '—',
      valueSm: true,
      meta: 'Promedio general',
    },
  ]
}

function totals(rows: Record<string, unknown>[]): ReportTotalCell[] {
  const monto = rows.reduce((sum, r) => sum + Number(r.total), 0)
  const items = rows.reduce((sum, r) => sum + Number(r.items_count), 0)
  return [
    { label: 'Ventas', value: String(rows.length) },
    { label: 'Ítems', value: String(items) },
    { label: 'Σ monto', value: formatMoney(monto), accent: true },
  ]
}
</script>

<template>
  <ReporteGenericView
    tipo="ventas"
    title="Reporte de ventas"
    subtitle="Historial de ventas registradas"
    icon="mdi-cash-register"
    :loader="reportesService.getVentas"
    :headers="headers"
    :prepare="prepare"
    :summary="summary"
    :totals="totals"
    table-title="Ventas"
    table-subtitle="Listado completo de ventas"
    search-label="Buscar venta o cliente..."
    empty-subtitle="No hay ventas registradas."
  >
    <template #item.codigo="{ value }">
      <span class="font-weight-medium">{{ value }}</span>
    </template>

    <template #item.cliente_nombre="{ value }">
      <span class="cell-ellipsis" :title="String(value ?? '')">{{ value }}</span>
    </template>

    <template #item.fecha="{ value }">
      <span class="text-caption text-medium-emphasis">
        {{ value ? formatDateCompact(String(value)) : '—' }}
      </span>
    </template>

    <template #item.estado="{ value }">
      <v-chip
        :color="ESTADO_VENTA_COLORS[String(value)] ?? 'default'"
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
