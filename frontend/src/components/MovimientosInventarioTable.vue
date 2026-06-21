<script setup lang="ts">
import { computed } from 'vue'
import BaseDataTable, { type TableHeader } from '@/components/BaseDataTable.vue'
import { formatDateCompact, formatInteger } from '@/utils/format'
import {
  TIPO_MOVIMIENTO_CONFIG,
  isMovimientoEntrada,
  type MovimientoInventarioRow,
} from '@/utils/inventario-movimientos'
import type { TipoMovimiento } from '@/types/inventario.types'

const props = withDefaults(
  defineProps<{
    items: MovimientoInventarioRow[]
    loading?: boolean
    title?: string
    subtitle?: string
    search?: string
    searchLabel?: string
    emptyTitle?: string
    emptySubtitle?: string
    showReferencia?: boolean
    showAlmacen?: boolean
    showProducto?: boolean
    showStock?: boolean
    showSearch?: boolean
    compact?: boolean
  }>(),
  {
    loading: false,
    title: 'Movimientos',
    subtitle: 'Historial de movimientos de inventario',
    search: '',
    searchLabel: 'Buscar movimiento...',
    emptyTitle: 'Sin movimientos',
    emptySubtitle: 'Los movimientos aparecerán aquí al registrar operaciones o confirmar recepciones.',
    showReferencia: true,
    showAlmacen: true,
    showProducto: true,
    showStock: true,
    showSearch: true,
    compact: false,
  },
)

const emit = defineEmits<{
  'update:search': [value: string]
  refresh: []
}>()

const searchModel = computed({
  get: () => props.search,
  set: (value: string) => emit('update:search', value),
})

const headers = computed((): TableHeader[] => {
  const list: TableHeader[] = [{ title: 'Tipo', key: 'tipo', width: props.compact ? 96 : 108 }]
  if (props.showProducto) list.push({ title: 'Producto', key: 'producto_nombre' })
  if (props.showAlmacen) list.push({ title: 'Almacén', key: 'almacen_nombre', width: 130 })
  list.push({ title: 'Cant.', key: 'cantidad', align: 'end' as const, width: 72 })
  if (props.showStock) {
    list.push({
      title: 'Stock',
      key: 'stock',
      align: 'center' as const,
      width: 96,
      sortable: false,
    })
  }
  if (props.showReferencia) list.push({ title: 'Origen / Ref.', key: 'referencia_label', width: 160 })
  list.push({ title: 'Fecha', key: 'creado_en', width: 130 })
  return list
})

function cantidadClass(tipo: TipoMovimiento): string {
  if (isMovimientoEntrada(tipo)) return 'text-success'
  if (tipo === 'SALIDA' || tipo === 'AJUSTE_NEGATIVO' || tipo === 'TRANSFERENCIA_SALIDA') return 'text-error'
  return ''
}
</script>

<template>
  <BaseDataTable
    v-model:search="searchModel"
    :items="items as unknown as Record<string, unknown>[]"
    :headers="headers"
    :loading="loading"
    :title="title"
    :subtitle="subtitle"
    :search-label="searchLabel"
    :show-search="showSearch"
    :empty-title="emptyTitle"
    :empty-subtitle="emptySubtitle"
  >
    <template #actions>
      <slot name="actions">
        <v-btn
          icon="mdi-refresh"
          variant="text"
          size="small"
          :loading="loading"
          aria-label="Actualizar movimientos"
          @click="emit('refresh')"
        />
      </slot>
    </template>

    <template #item.tipo="{ value }">
      <v-chip
        :color="TIPO_MOVIMIENTO_CONFIG[value as TipoMovimiento]?.color ?? 'default'"
        size="x-small"
        variant="tonal"
        label
      >
        {{ TIPO_MOVIMIENTO_CONFIG[value as TipoMovimiento]?.label ?? value }}
      </v-chip>
    </template>

    <template #item.producto_nombre="{ item }">
      <span class="cell-ellipsis cell-ellipsis--wide" :title="item.producto_nombre ?? ''">
        {{ item.producto_nombre }}
      </span>
    </template>

    <template #item.almacen_nombre="{ value }">
      <span class="cell-ellipsis" :title="value ?? ''">{{ value }}</span>
    </template>

    <template #item.cantidad="{ value, item }">
      <span class="font-weight-medium" :class="cantidadClass(item.tipo as TipoMovimiento)">
        {{ isMovimientoEntrada(item.tipo as TipoMovimiento) ? '+' : '' }}{{ formatInteger(value) }}
      </span>
    </template>

    <template #item.stock="{ item }">
      <span class="stock-delta text-caption">
        {{ formatInteger(item.cantidad_anterior) }}
        <v-icon icon="mdi-arrow-right-thin" size="12" />
        <strong>{{ formatInteger(item.cantidad_nueva) }}</strong>
      </span>
    </template>

    <template #item.referencia_label="{ value }">
      <span class="cell-ellipsis cell-ellipsis--ref text-medium-emphasis" :title="value ?? ''">
        {{ value || '—' }}
      </span>
    </template>

    <template #item.creado_en="{ value }">
      <span class="text-caption text-medium-emphasis">{{ formatDateCompact(value) }}</span>
    </template>
  </BaseDataTable>
</template>

<style scoped>
.cell-ellipsis {
  display: block;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-ellipsis--wide {
  max-width: 180px;
}

.cell-ellipsis--ref {
  max-width: 160px;
}

.stock-delta {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: rgba(var(--v-theme-on-surface), 0.6);
  white-space: nowrap;
}
</style>
