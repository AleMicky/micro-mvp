<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { formatInteger } from '@/utils/format'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen, Existencia } from '@/types/inventario.types'

const appStore = useAppStore()

const items = ref<Existencia[]>([])
const productos = ref<Producto[]>([])
const almacenes = ref<Almacen[]>([])
const loading = ref(false)
const search = ref('')
const filterProducto = ref<number | null>(null)
const filterAlmacen = ref<number | null>(null)

const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))
const almacenMap = computed(() => Object.fromEntries(almacenes.value.map((a) => [a.id, a.nombre])))

const stats = computed(() => {
  const bajo = items.value.filter((item) => getStockStatus(item) === 'bajo').length
  const total = items.value.reduce((sum, item) => sum + Number(item.cantidad_actual), 0)
  return { filas: items.value.length, bajo, total: Math.trunc(total) }
})

const hasFilters = computed(() => filterProducto.value !== null || filterAlmacen.value !== null)

const headers = [
  { title: 'Producto', key: 'producto_id' },
  { title: 'Almacén', key: 'almacen_id' },
  { title: 'Cant.', key: 'cantidad_actual', align: 'end' as const, width: 72 },
  { title: 'Mín.', key: 'stock_minimo', align: 'end' as const, width: 64 },
  { title: 'Máx.', key: 'stock_maximo', align: 'end' as const, width: 64 },
  { title: 'Estado', key: 'stock_status', width: 96, sortable: false },
]

function getStockStatus(item: Existencia) {
  const actual = Number(item.cantidad_actual)
  const minimo = Number(item.stock_minimo)
  if (minimo > 0 && actual <= minimo) return 'bajo'
  return 'ok'
}

function stockLevel(item: Existencia): number {
  const max = item.stock_maximo ? Number(item.stock_maximo) : Number(item.stock_minimo) * 2 || 100
  if (max <= 0) return 0
  return Math.min(100, Math.round((Number(item.cantidad_actual) / max) * 100))
}

function clearFilters() {
  filterProducto.value = null
  filterAlmacen.value = null
}

async function loadCatalogos() {
  const [productosRes, almacenesRes] = await Promise.all([
    catalogosService.getProductos(),
    inventarioService.getAlmacenes(),
  ])
  productos.value = productosRes.data
  almacenes.value = almacenesRes.data
}

async function loadExistencias() {
  loading.value = true
  try {
    if (filterProducto.value) {
      const { data } = await inventarioService.getExistenciasByProducto(filterProducto.value)
      items.value = data
    } else if (filterAlmacen.value) {
      const { data } = await inventarioService.getExistenciasByAlmacen(filterAlmacen.value)
      items.value = data
    } else {
      const { data } = await inventarioService.getExistencias()
      items.value = data
    }
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

watch([filterProducto, filterAlmacen], loadExistencias)

onMounted(async () => {
  try {
    await loadCatalogos()
    await loadExistencias()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  }
})
</script>

<template>
  <div class="existencias-page">
    <PageHeader
      title="Existencias"
      subtitle="Consulta de stock por producto y almacén"
      icon="mdi-package-check"
    >
      <template #actions>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="loading"
          @click="loadExistencias"
        >
          Actualizar
        </v-btn>
      </template>
    </PageHeader>

    <div class="stats-row">
      <div class="stat-pill">
        <span class="stat-pill__value">{{ stats.filas }}</span>
        <span class="stat-pill__label">Registros</span>
      </div>
      <div class="stat-pill">
        <span class="stat-pill__value">{{ formatInteger(stats.total) }}</span>
        <span class="stat-pill__label">Unidades totales</span>
      </div>
      <div class="stat-pill" :class="{ 'stat-pill--warn': stats.bajo > 0 }">
        <span class="stat-pill__value">{{ stats.bajo }}</span>
        <span class="stat-pill__label">Stock bajo</span>
      </div>
    </div>

    <div class="filters-panel">
      <div class="filters-bar">
        <v-autocomplete
          v-model="filterProducto"
          :items="productos"
          item-title="nombre"
          item-value="id"
          label="Producto"
          clearable
          hide-details
          density="compact"
          prepend-inner-icon="mdi-package-variant"
          class="filters-bar__field filters-bar__field--producto"
          @update:model-value="filterAlmacen = null"
        />
        <v-autocomplete
          v-model="filterAlmacen"
          :items="almacenes"
          item-title="nombre"
          item-value="id"
          label="Almacén"
          clearable
          hide-details
          density="compact"
          prepend-inner-icon="mdi-warehouse"
          class="filters-bar__field filters-bar__field--almacen"
          @update:model-value="filterProducto = null"
        />
        <v-btn
          v-if="hasFilters"
          size="small"
          variant="text"
          prepend-icon="mdi-filter-off-outline"
          class="filters-bar__clear"
          @click="clearFilters"
        >
          Limpiar
        </v-btn>
      </div>
    </div>

    <BaseDataTable
      v-model:search="search"
      :items="items as Record<string, unknown>[]"
      :headers="headers"
      :loading="loading"
      title="Inventario"
      subtitle="Existencias actuales"
      search-label="Buscar producto o almacén..."
      empty-subtitle="Registra ingresos de stock para ver existencias."
    >
      <template #item.producto_id="{ value }">
        <span class="cell-ellipsis cell-ellipsis--wide" :title="productoMap[value] ?? String(value)">
          {{ productoMap[value] ?? value }}
        </span>
      </template>

      <template #item.almacen_id="{ value }">
        <span class="cell-ellipsis" :title="almacenMap[value] ?? String(value)">
          {{ almacenMap[value] ?? value }}
        </span>
      </template>

      <template #item.cantidad_actual="{ value, item }">
        <div class="qty-cell">
          <span
            class="qty-cell__value font-weight-medium"
            :class="{ 'text-warning': getStockStatus(item as Existencia) === 'bajo' }"
          >
            {{ formatInteger(value) }}
          </span>
          <v-progress-linear
            :model-value="stockLevel(item as Existencia)"
            :color="getStockStatus(item as Existencia) === 'bajo' ? 'warning' : 'success'"
            height="3"
            rounded
            class="qty-cell__bar"
          />
        </div>
      </template>

      <template #item.stock_minimo="{ value }">
        <span class="text-caption">{{ formatInteger(value) }}</span>
      </template>

      <template #item.stock_maximo="{ value }">
        <span class="text-caption text-medium-emphasis">{{ value != null ? formatInteger(value) : '—' }}</span>
      </template>

      <template #item.stock_status="{ item }">
        <v-chip
          :color="getStockStatus(item as Existencia) === 'bajo' ? 'warning' : 'success'"
          size="x-small"
          variant="tonal"
          label
        >
          {{ getStockStatus(item as Existencia) === 'bajo' ? 'Bajo' : 'OK' }}
        </v-chip>
      </template>
    </BaseDataTable>
  </div>
</template>

<style scoped>
.existencias-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.stat-pill {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: #fff;
}

.stat-pill--warn {
  border-color: rgba(var(--v-theme-warning), 0.35);
  background: rgba(var(--v-theme-warning), 0.06);
}

.stat-pill__value {
  font-size: 1rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  color: rgb(var(--v-theme-on-surface));
}

.stat-pill--warn .stat-pill__value {
  color: rgb(var(--v-theme-warning));
}

.stat-pill__label {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.filters-panel {
  padding: 10px 12px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: #fff;
}

.filters-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.filters-bar__field--producto {
  flex: 1 1 280px;
  min-width: 240px;
  max-width: 480px;
}

.filters-bar__field--almacen {
  flex: 1 1 220px;
  min-width: 200px;
  max-width: 420px;
}

.filters-bar__clear {
  flex-shrink: 0;
}

.filters-bar__field :deep(.v-autocomplete__selection-text),
.filters-bar__field :deep(.v-field-label) {
  overflow: visible;
  text-overflow: clip;
  white-space: nowrap;
}

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

.qty-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
  min-width: 48px;
}

.qty-cell__value {
  font-variant-numeric: tabular-nums;
}

.qty-cell__bar {
  width: 48px;
  opacity: 0.85;
}

@media (max-width: 600px) {
  .filters-bar__field--producto,
  .filters-bar__field--almacen {
    flex: 1 1 100%;
    min-width: 100%;
    max-width: 100%;
  }

  .cell-ellipsis,
  .cell-ellipsis--wide {
    max-width: 100px;
  }
}
</style>
