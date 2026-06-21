<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { reportesService } from '@/services/reportes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { formatDateCompact, formatMoney } from '@/utils/format'
import {
  ESTADO_FINANZA_COLORS,
  type CuentaPorCobrar,
  type CuentaPorPagar,
} from '@/types/finanzas.types'

const appStore = useAppStore()
const loading = ref(false)
const cxc = ref<CuentaPorCobrar[]>([])
const cxp = ref<CuentaPorPagar[]>([])
const searchCxc = ref('')
const searchCxp = ref('')

const headers = [
  { title: 'Código', key: 'codigo', width: 108 },
  { title: 'Monto', key: 'monto', align: 'end' as const, width: 100 },
  { title: 'Saldo', key: 'saldo', align: 'end' as const, width: 100 },
  { title: 'Estado', key: 'estado', width: 100, sortable: false },
  { title: 'Vence', key: 'fecha_vencimiento', width: 110 },
  { title: 'Descripción', key: 'descripcion' },
]

function sumField(rows: { monto?: unknown; saldo?: unknown }[], field: 'monto' | 'saldo'): number {
  return rows.reduce((sum, r) => sum + Number(r[field] ?? 0), 0)
}

function countPendientes(rows: { estado?: string }[]): number {
  return rows.filter((r) => r.estado === 'PENDIENTE' || r.estado === 'PARCIAL' || r.estado === 'VENCIDO').length
}

const resumenCxc = computed(() => ({
  filas: cxc.value.length,
  monto: sumField(cxc.value, 'monto'),
  saldo: sumField(cxc.value, 'saldo'),
  pendientes: countPendientes(cxc.value),
}))

const resumenCxp = computed(() => ({
  filas: cxp.value.length,
  monto: sumField(cxp.value, 'monto'),
  saldo: sumField(cxp.value, 'saldo'),
  pendientes: countPendientes(cxp.value),
}))

const posicionNeta = computed(() => resumenCxc.value.saldo - resumenCxp.value.saldo)

async function loadData() {
  loading.value = true
  try {
    const { data } = await reportesService.getFinanzas()
    cxc.value = (data as { cuentas_por_cobrar?: CuentaPorCobrar[] }).cuentas_por_cobrar ?? []
    cxp.value = (data as { cuentas_por_pagar?: CuentaPorPagar[] }).cuentas_por_pagar ?? []
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div class="reporte-page">
    <PageHeader
      title="Reporte financiero"
      subtitle="Cuentas por cobrar y cuentas por pagar"
      icon="mdi-cash-multiple"
    >
      <template #actions>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="loading"
          @click="loadData"
        >
          Actualizar
        </v-btn>
      </template>
    </PageHeader>

    <div class="reporte-summary reporte-summary--4">
      <div class="summary-card summary-card--accent">
        <span class="summary-card__label">Por cobrar</span>
        <span class="summary-card__value summary-card__value--sm">{{ formatMoney(resumenCxc.saldo) }}</span>
        <span class="summary-card__meta">{{ resumenCxc.filas }} cuenta(s) · {{ resumenCxc.pendientes }} pendiente(s)</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Monto CXC</span>
        <span class="summary-card__value summary-card__value--sm">{{ formatMoney(resumenCxc.monto) }}</span>
        <span class="summary-card__meta">Cartera de clientes</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Por pagar</span>
        <span class="summary-card__value summary-card__value--sm">{{ formatMoney(resumenCxp.saldo) }}</span>
        <span class="summary-card__meta">{{ resumenCxp.filas }} cuenta(s) · {{ resumenCxp.pendientes }} pendiente(s)</span>
      </div>

      <div class="summary-card" :class="{ 'summary-card--product': posicionNeta >= 0 }">
        <span class="summary-card__label">Posición neta</span>
        <span
          class="summary-card__value summary-card__value--sm"
          :class="posicionNeta >= 0 ? 'text-success' : 'text-error'"
        >
          {{ formatMoney(posicionNeta) }}
        </span>
        <span class="summary-card__meta">CXC − CXP</span>
      </div>
    </div>

    <div class="reporte-financiero-grid">
      <div class="reporte-table-wrap">
        <BaseDataTable
          v-model:search="searchCxc"
          :items="cxc as unknown as Record<string, unknown>[]"
          :headers="headers"
          :loading="loading"
          title="Cuentas por cobrar"
          subtitle="Cartera de clientes"
          search-label="Buscar CXC..."
          empty-subtitle="No hay cuentas por cobrar registradas."
        >
          <template #item.codigo="{ value }">
            <span class="font-weight-medium">{{ value }}</span>
          </template>

          <template #item.monto="{ value }">
            <span class="text-medium-emphasis">{{ formatMoney(value) }}</span>
          </template>

          <template #item.saldo="{ value }">
            <span class="font-weight-medium">{{ formatMoney(value) }}</span>
          </template>

          <template #item.estado="{ value }">
            <v-chip
              :color="ESTADO_FINANZA_COLORS[String(value)] ?? 'default'"
              size="x-small"
              variant="tonal"
              label
            >
              {{ value }}
            </v-chip>
          </template>

          <template #item.fecha_vencimiento="{ value }">
            <span class="text-caption text-medium-emphasis">
              {{ value ? formatDateCompact(String(value)) : '—' }}
            </span>
          </template>

          <template #item.descripcion="{ value }">
            <span class="cell-ellipsis" :title="String(value ?? '')">{{ value || '—' }}</span>
          </template>
        </BaseDataTable>

        <div v-if="cxc.length" class="totals-bar">
          <div class="totals-bar__cell">
            <span class="totals-bar__label">Cuentas</span>
            <strong class="totals-bar__value">{{ resumenCxc.filas }}</strong>
          </div>
          <div class="totals-bar__cell">
            <span class="totals-bar__label">Σ monto</span>
            <strong class="totals-bar__value">{{ formatMoney(resumenCxc.monto) }}</strong>
          </div>
          <div class="totals-bar__cell">
            <span class="totals-bar__label">Σ saldo</span>
            <strong class="totals-bar__value totals-bar__value--accent">{{ formatMoney(resumenCxc.saldo) }}</strong>
          </div>
        </div>
      </div>

      <div class="reporte-table-wrap">
        <BaseDataTable
          v-model:search="searchCxp"
          :items="cxp as unknown as Record<string, unknown>[]"
          :headers="headers"
          :loading="loading"
          title="Cuentas por pagar"
          subtitle="Obligaciones con proveedores"
          search-label="Buscar CXP..."
          empty-subtitle="No hay cuentas por pagar registradas."
        >
          <template #item.codigo="{ value }">
            <span class="font-weight-medium">{{ value }}</span>
          </template>

          <template #item.monto="{ value }">
            <span class="text-medium-emphasis">{{ formatMoney(value) }}</span>
          </template>

          <template #item.saldo="{ value }">
            <span class="font-weight-medium">{{ formatMoney(value) }}</span>
          </template>

          <template #item.estado="{ value }">
            <v-chip
              :color="ESTADO_FINANZA_COLORS[String(value)] ?? 'default'"
              size="x-small"
              variant="tonal"
              label
            >
              {{ value }}
            </v-chip>
          </template>

          <template #item.fecha_vencimiento="{ value }">
            <span class="text-caption text-medium-emphasis">
              {{ value ? formatDateCompact(String(value)) : '—' }}
            </span>
          </template>

          <template #item.descripcion="{ value }">
            <span class="cell-ellipsis" :title="String(value ?? '')">{{ value || '—' }}</span>
          </template>
        </BaseDataTable>

        <div v-if="cxp.length" class="totals-bar">
          <div class="totals-bar__cell">
            <span class="totals-bar__label">Cuentas</span>
            <strong class="totals-bar__value">{{ resumenCxp.filas }}</strong>
          </div>
          <div class="totals-bar__cell">
            <span class="totals-bar__label">Σ monto</span>
            <strong class="totals-bar__value">{{ formatMoney(resumenCxp.monto) }}</strong>
          </div>
          <div class="totals-bar__cell">
            <span class="totals-bar__label">Σ saldo</span>
            <strong class="totals-bar__value totals-bar__value--accent">{{ formatMoney(resumenCxp.saldo) }}</strong>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@/styles/reportes-shared.css';

.reporte-financiero-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  align-items: start;
}

@media (max-width: 960px) {
  .reporte-financiero-grid {
    grid-template-columns: 1fr;
  }
}
</style>
