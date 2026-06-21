<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { api, getErrorMessage } from '@/services/api'
import { ventasService } from '@/services/ventas.service'
import { useAppStore } from '@/stores/app.store'
import { formatDateCompact, formatMoney } from '@/utils/format'
import { ESTADO_VENTA_COLORS, type Venta } from '@/types/ventas.types'

interface ReporteDia {
  fecha: string
  total_ventas: number
  monto_total: number
  ventas: Venta[]
}

const appStore = useAppStore()
const reporte = ref<ReporteDia | null>(null)
const loading = ref(false)
const search = ref('')
const fecha = ref(new Date().toISOString().slice(0, 10))
const clienteMap = ref<Record<number, string>>({})

const ticketPromedio = computed(() => {
  if (!reporte.value?.total_ventas) return null
  return reporte.value.monto_total / reporte.value.total_ventas
})

const tableRows = computed(() =>
  (reporte.value?.ventas ?? []).map((v) => ({
    ...v,
    cliente_nombre: clienteMap.value[v.cliente_id] ?? `Cliente ${v.cliente_id}`,
    items_count: v.detalles?.length ?? 0,
  })),
)

const headers = [
  { title: 'Número', key: 'codigo', width: 108 },
  { title: 'Cliente', key: 'cliente_nombre' },
  { title: 'Estado', key: 'estado', width: 108, sortable: false },
  { title: 'Ítems', key: 'items_count', align: 'end' as const, width: 64, sortable: false },
  { title: 'Total', key: 'total', align: 'end' as const, width: 108 },
  { title: 'Hora', key: 'creado_en', width: 120 },
]

function formatFechaLabel(value: string): string {
  return new Date(`${value}T12:00:00`).toLocaleDateString('es-BO', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

async function loadClientes() {
  try {
    const { data } = await ventasService.getClientes()
    clienteMap.value = Object.fromEntries(data.map((c) => [c.id, c.nombre]))
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  }
}

async function cargar() {
  loading.value = true
  try {
    const { data } = await api.get<ReporteDia>('/ventas/ventas/reporte/dia', { params: { fecha: fecha.value } })
    reporte.value = data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

watch(fecha, cargar)

onMounted(async () => {
  await loadClientes()
  await cargar()
})
</script>

<template>
  <div class="reporte-page">
    <PageHeader
      title="Ventas del día"
      subtitle="Resumen y detalle de ventas por fecha"
      icon="mdi-calendar-today"
    >
      <template #actions>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="loading"
          @click="cargar"
        >
          Actualizar
        </v-btn>
      </template>
    </PageHeader>

    <v-card class="reporte-filter" border elevation="0">
      <div class="reporte-filter__row">
        <v-text-field
          v-model="fecha"
          type="date"
          label="Fecha"
          density="compact"
          hide-details
          prepend-inner-icon="mdi-calendar"
          class="reporte-filter__field"
        />
      </div>
    </v-card>

    <div v-if="reporte" class="reporte-summary reporte-summary--3">
      <div class="summary-card">
        <span class="summary-card__label">Ventas</span>
        <span class="summary-card__value">{{ reporte.total_ventas }}</span>
        <span class="summary-card__meta">{{ formatFechaLabel(reporte.fecha) }}</span>
      </div>

      <div class="summary-card summary-card--accent">
        <span class="summary-card__label">Monto total</span>
        <span class="summary-card__value summary-card__value--sm">{{ formatMoney(reporte.monto_total) }}</span>
        <span class="summary-card__meta">Confirmadas / facturadas</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Ticket promedio</span>
        <span class="summary-card__value summary-card__value--sm">{{ formatMoney(ticketPromedio) }}</span>
        <span class="summary-card__meta">Por venta</span>
      </div>
    </div>

    <div class="reporte-table-wrap">
      <BaseDataTable
        v-model:search="search"
        :items="tableRows as unknown as Record<string, unknown>[]"
        :headers="headers"
        :loading="loading"
        title="Detalle de ventas"
        :subtitle="reporte ? `Ventas del ${formatFechaLabel(reporte.fecha)}` : 'Selecciona una fecha'"
        search-label="Buscar venta o cliente..."
        empty-title="Sin ventas"
        empty-subtitle="No se registraron ventas en la fecha seleccionada."
      >
        <template #item.codigo="{ value }">
          <span class="font-weight-medium">{{ value }}</span>
        </template>

        <template #item.cliente_nombre="{ value }">
          <span class="cell-ellipsis" :title="String(value ?? '')">{{ value }}</span>
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

        <template #item.creado_en="{ value }">
          <span class="text-caption text-medium-emphasis">{{ formatDateCompact(String(value)) }}</span>
        </template>
      </BaseDataTable>

      <div v-if="reporte && tableRows.length" class="totals-bar">
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Ventas</span>
          <strong class="totals-bar__value">{{ reporte.total_ventas }}</strong>
        </div>
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Ítems</span>
          <strong class="totals-bar__value">
            {{ tableRows.reduce((s, v) => s + Number(v.items_count), 0) }}
          </strong>
        </div>
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Σ monto</span>
          <strong class="totals-bar__value totals-bar__value--accent">
            {{ formatMoney(reporte.monto_total) }}
          </strong>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@/styles/reportes-shared.css';
</style>
