<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable, { type TableHeader } from '@/components/BaseDataTable.vue'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { reportesService } from '@/services/reportes.service'

export interface ReportSummaryCell {
  label: string
  value: string
  meta?: string
  variant?: 'product' | 'accent'
  valueSm?: boolean
}

export interface ReportTotalCell {
  label: string
  value: string
  accent?: boolean
  colorClass?: string
}

const props = withDefaults(
  defineProps<{
    tipo: string
    title: string
    subtitle?: string
    icon?: string
    loader: () => ReturnType<typeof reportesService.getStock>
    headers: TableHeader[]
    prepare?: (items: unknown[]) => Promise<Record<string, unknown>[]> | Record<string, unknown>[]
    summary?: (rows: Record<string, unknown>[]) => ReportSummaryCell[]
    totals?: (rows: Record<string, unknown>[]) => ReportTotalCell[]
    tableTitle?: string
    tableSubtitle?: string
    emptyTitle?: string
    emptySubtitle?: string
    searchLabel?: string
    showSummary?: boolean
  }>(),
  {
    subtitle: undefined,
    icon: 'mdi-file-chart-outline',
    tableTitle: 'Detalle',
    tableSubtitle: 'Registros del reporte',
    emptyTitle: 'Sin registros',
    emptySubtitle: 'No hay datos para mostrar en este reporte.',
    searchLabel: 'Buscar...',
    showSummary: true,
  },
)

const appStore = useAppStore()
const loading = ref(false)
const search = ref('')
const totalRegistros = ref(0)
const rows = ref<Record<string, unknown>[]>([])

const summaryCells = computed(() => (props.showSummary && props.summary ? props.summary(rows.value) : []))
const totalsCells = computed(() => (props.totals ? props.totals(rows.value) : []))
const pageSubtitle = computed(() => props.subtitle ?? `Reporte de ${props.tipo}`)

async function loadData() {
  loading.value = true
  try {
    const { data } = await props.loader()
    const payload = data as { items?: unknown[]; total?: number }
    const raw = payload.items ?? []
    totalRegistros.value = payload.total ?? raw.length
    rows.value = props.prepare ? await props.prepare(raw) : (raw as Record<string, unknown>[])
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
    <PageHeader :title="title" :subtitle="pageSubtitle" :icon="icon">
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

    <slot name="filters" />

    <div v-if="summaryCells.length" class="reporte-summary">
      <div
        v-for="(cell, idx) in summaryCells"
        :key="idx"
        class="summary-card"
        :class="{
          'summary-card--product': cell.variant === 'product',
          'summary-card--accent': cell.variant === 'accent',
        }"
      >
        <span class="summary-card__label">{{ cell.label }}</span>
        <span
          v-if="cell.variant === 'product'"
          class="summary-card__title"
          :title="cell.value"
        >
          {{ cell.value }}
        </span>
        <span
          v-else
          class="summary-card__value"
          :class="{ 'summary-card__value--sm': cell.valueSm }"
        >
          {{ cell.value }}
        </span>
        <span v-if="cell.meta" class="summary-card__meta text-caption text-medium-emphasis">
          {{ cell.meta }}
        </span>
      </div>
    </div>

    <div class="reporte-table-wrap">
      <BaseDataTable
        v-model:search="search"
        :items="rows"
        :headers="headers"
        :loading="loading"
        :title="tableTitle"
        :subtitle="tableSubtitle"
        :search-label="searchLabel"
        :empty-title="emptyTitle"
        :empty-subtitle="emptySubtitle"
      >
        <template #actions>
          <slot name="table-actions" />
        </template>

        <template v-for="(_, name) in $slots" #[name]="slotData">
          <slot v-if="!['filters', 'table-actions'].includes(String(name))" :name="name" v-bind="slotData ?? {}" />
        </template>
      </BaseDataTable>

      <div v-if="totalsCells.length" class="totals-bar">
        <div v-for="(cell, idx) in totalsCells" :key="idx" class="totals-bar__cell">
          <span class="totals-bar__label">{{ cell.label }}</span>
          <strong
            class="totals-bar__value"
            :class="[
              cell.accent ? 'totals-bar__value--accent' : '',
              cell.colorClass,
            ]"
          >
            {{ cell.value }}
          </strong>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@/styles/reportes-shared.css';
</style>
