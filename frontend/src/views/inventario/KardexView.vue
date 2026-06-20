<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { formatDateCompact, formatInteger, formatMoney } from '@/utils/format'
import type { Producto } from '@/types/catalogos.types'
import type { Existencia, MovimientoInventario, TipoMovimiento } from '@/types/inventario.types'

const appStore = useAppStore()

const productos = ref<Producto[]>([])
const almacenes = ref<{ id: number; nombre: string }[]>([])
const selectedProducto = ref<number | null>(null)
const movimientos = ref<MovimientoInventario[]>([])
const existencias = ref<Existencia[]>([])
const totalMovimientos = ref(0)
const loading = ref(false)
const search = ref('')

const productoSeleccionado = computed(() =>
  productos.value.find((p) => p.id === selectedProducto.value) ?? null,
)

const almacenMap = computed(() => Object.fromEntries(almacenes.value.map((a) => [a.id, a.nombre])))

const stockTotal = computed(() =>
  Math.trunc(existencias.value.reduce((sum, e) => sum + Number(e.cantidad_actual), 0)),
)

const resumenPrecios = computed(() => {
  const producto = productoSeleccionado.value
  if (!producto) return null

  const precioVenta = producto.precio_actual ?? null
  const costoUnitario = producto.precio_base ?? null
  const stock = stockTotal.value

  return {
    precioVenta,
    costoUnitario,
    valorVenta: precioVenta != null ? stock * precioVenta : null,
    valorCosto: costoUnitario != null ? stock * costoUnitario : null,
  }
})

const movimientosVisibles = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return movimientos.value
  return movimientos.value.filter((m) => {
    const texto = [
      m.tipo,
      almacenMap.value[m.almacen_id],
      m.observaciones,
      formatInteger(m.cantidad),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return texto.includes(term)
  })
})

const totalesKardex = computed(() => {
  const costoUnit = productoSeleccionado.value?.precio_base
  const ventaUnit = productoSeleccionado.value?.precio_actual
  let sumCantidad = 0
  let sumCosto = 0
  let sumVenta = 0
  let filasCosto = 0
  let filasVenta = 0

  for (const m of movimientosVisibles.value) {
    const qty = Number(m.cantidad)
    if (Number.isFinite(qty)) sumCantidad += qty

    const vc = valorMovimiento(m.cantidad, costoUnit)
    const vv = valorMovimiento(m.cantidad, ventaUnit)
    if (vc != null) {
      sumCosto += vc
      filasCosto++
    }
    if (vv != null) {
      sumVenta += vv
      filasVenta++
    }
  }

  return {
    filas: movimientosVisibles.value.length,
    sumCantidad: Math.trunc(sumCantidad),
    sumCosto: filasCosto ? sumCosto : null,
    sumVenta: filasVenta ? sumVenta : null,
  }
})

const headers = [
  { title: 'Tipo', key: 'tipo', width: 108 },
  { title: 'Almacén', key: 'almacen_id' },
  { title: 'Cant.', key: 'cantidad', align: 'end' as const, width: 64 },
  { title: 'Stock', key: 'stock', align: 'center' as const, width: 96, sortable: false },
  { title: 'Costo', key: 'valor_costo', align: 'end' as const, width: 88, sortable: false },
  { title: 'Precio', key: 'valor_venta', align: 'end' as const, width: 88, sortable: false },
  { title: 'Obs.', key: 'observaciones', width: 120 },
  { title: 'Fecha', key: 'creado_en', width: 130 },
]

const tipoConfig: Record<TipoMovimiento, { color: string; label: string }> = {
  INGRESO: { color: 'success', label: 'Ingreso' },
  SALIDA: { color: 'error', label: 'Salida' },
  AJUSTE_POSITIVO: { color: 'info', label: 'Ajuste +' },
  AJUSTE_NEGATIVO: { color: 'warning', label: 'Ajuste −' },
  TRANSFERENCIA_SALIDA: { color: 'secondary', label: 'Trans. salida' },
  TRANSFERENCIA_ENTRADA: { color: 'primary', label: 'Trans. entrada' },
}

function valorMovimiento(cantidad: unknown, unitario: number | null | undefined): number | null {
  if (unitario == null || unitario <= 0) return null
  const qty = Number(cantidad)
  if (!Number.isFinite(qty)) return null
  return qty * unitario
}

function isEntrada(tipo: TipoMovimiento): boolean {
  return tipo === 'INGRESO' || tipo === 'AJUSTE_POSITIVO' || tipo === 'TRANSFERENCIA_ENTRADA'
}

function cantidadClass(tipo: TipoMovimiento): string {
  if (isEntrada(tipo)) return 'text-success'
  if (tipo === 'SALIDA' || tipo === 'AJUSTE_NEGATIVO' || tipo === 'TRANSFERENCIA_SALIDA') return 'text-error'
  return ''
}

async function loadCatalogos() {
  try {
    const [productosRes, almacenesRes] = await Promise.all([
      catalogosService.getProductos(),
      inventarioService.getAlmacenes(),
    ])
    productos.value = productosRes.data
    almacenes.value = almacenesRes.data.map((a) => ({ id: a.id, nombre: a.nombre }))
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  }
}

async function loadKardex() {
  if (!selectedProducto.value) {
    movimientos.value = []
    existencias.value = []
    totalMovimientos.value = 0
    return
  }

  loading.value = true
  try {
    const [kardexRes, existenciasRes] = await Promise.all([
      inventarioService.getKardex(selectedProducto.value),
      inventarioService.getExistenciasByProducto(selectedProducto.value),
    ])
    movimientos.value = kardexRes.data.movimientos
    totalMovimientos.value = kardexRes.data.total_movimientos
    existencias.value = existenciasRes.data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

watch(selectedProducto, loadKardex)

onMounted(loadCatalogos)
</script>

<template>
  <div class="kardex-page">
    <PageHeader
      title="Kardex"
      subtitle="Historial de movimientos y valorización por producto"
      icon="mdi-file-document-outline"
    >
      <template #actions>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="loading"
          :disabled="!selectedProducto"
          @click="loadKardex"
        >
          Actualizar
        </v-btn>
      </template>
    </PageHeader>

    <v-card class="kardex-filter" border elevation="0">
      <v-autocomplete
        v-model="selectedProducto"
        :items="productos"
        item-title="nombre"
        item-value="id"
        label="Producto"
        density="compact"
        hide-details
        clearable
        prepend-inner-icon="mdi-package-variant-closed"
        placeholder="Buscar producto..."
        class="kardex-filter__field"
      >
        <template #item="{ props: itemProps, item }">
          <v-list-item v-bind="itemProps">
            <template #subtitle>
              {{ item.raw.codigo }}
              <span v-if="item.raw.precio_actual != null"> · {{ formatMoney(item.raw.precio_actual) }}</span>
            </template>
          </v-list-item>
        </template>
      </v-autocomplete>
    </v-card>

    <div v-if="productoSeleccionado" class="kardex-summary">
      <div class="summary-card summary-card--product">
        <span class="summary-card__label">Producto</span>
        <span class="summary-card__title">{{ productoSeleccionado.nombre }}</span>
        <span class="summary-card__meta text-caption text-medium-emphasis">{{ productoSeleccionado.codigo }}</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Stock total</span>
        <span class="summary-card__value">{{ formatInteger(stockTotal) }}</span>
        <span class="summary-card__meta">{{ totalMovimientos }} movimiento(s)</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Costo unit.</span>
        <span class="summary-card__value summary-card__value--sm">
          {{ formatMoney(resumenPrecios?.costoUnitario) }}
        </span>
        <span class="summary-card__meta">Inv. costo: {{ formatMoney(resumenPrecios?.valorCosto) }}</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">P. venta</span>
        <span class="summary-card__value summary-card__value--sm">
          {{ formatMoney(resumenPrecios?.precioVenta) }}
        </span>
        <span class="summary-card__meta">Inv. venta: {{ formatMoney(resumenPrecios?.valorVenta) }}</span>
      </div>
    </div>

    <div class="kardex-table-wrap">
    <BaseDataTable
      v-model:search="search"
      :items="movimientos as Record<string, unknown>[]"
      :headers="headers"
      :loading="loading"
      :show-search="!!selectedProducto"
      title="Movimientos"
      :subtitle="productoSeleccionado ? `Kardex de ${productoSeleccionado.nombre}` : 'Selecciona un producto'"
      search-label="Buscar movimiento..."
      empty-title="Selecciona un producto"
      empty-subtitle="Elige un producto para ver su kardex de movimientos."
    >
      <template #item.tipo="{ value }">
        <v-chip
          :color="tipoConfig[value as TipoMovimiento]?.color ?? 'default'"
          size="x-small"
          variant="tonal"
          label
        >
          {{ tipoConfig[value as TipoMovimiento]?.label ?? value }}
        </v-chip>
      </template>

      <template #item.almacen_id="{ value }">
        <span class="cell-ellipsis" :title="almacenMap[value] ?? String(value)">
          {{ almacenMap[value] ?? value }}
        </span>
      </template>

      <template #item.cantidad="{ value, item }">
        <span class="font-weight-medium" :class="cantidadClass(item.tipo as TipoMovimiento)">
          {{ formatInteger(value) }}
        </span>
      </template>

      <template #item.stock="{ item }">
        <span class="stock-delta text-caption">
          {{ formatInteger(item.cantidad_anterior) }}
          <v-icon icon="mdi-arrow-right-thin" size="12" />
          <strong>{{ formatInteger(item.cantidad_nueva) }}</strong>
        </span>
      </template>

      <template #item.valor_costo="{ item }">
        <span class="money-cell text-caption">
          {{ formatMoney(valorMovimiento(item.cantidad, productoSeleccionado?.precio_base)) }}
        </span>
      </template>

      <template #item.valor_venta="{ item }">
        <span class="money-cell text-caption font-weight-medium">
          {{ formatMoney(valorMovimiento(item.cantidad, productoSeleccionado?.precio_actual)) }}
        </span>
      </template>

      <template #item.observaciones="{ value }">
        <span class="cell-ellipsis text-medium-emphasis" :title="value ?? ''">
          {{ value || '—' }}
        </span>
      </template>

      <template #item.creado_en="{ value }">
        <span class="text-caption text-medium-emphasis">{{ formatDateCompact(value) }}</span>
      </template>
    </BaseDataTable>

    <div v-if="selectedProducto && movimientos.length" class="totals-bar">
      <div class="totals-bar__cell">
        <span class="totals-bar__label">Movimientos</span>
        <strong class="totals-bar__value">{{ totalesKardex.filas }}</strong>
      </div>
      <div class="totals-bar__cell">
        <span class="totals-bar__label">Σ cantidad</span>
        <strong class="totals-bar__value">{{ formatInteger(totalesKardex.sumCantidad) }}</strong>
      </div>
      <div class="totals-bar__cell">
        <span class="totals-bar__label">Σ costos</span>
        <strong class="totals-bar__value">{{ formatMoney(totalesKardex.sumCosto) }}</strong>
      </div>
      <div class="totals-bar__cell">
        <span class="totals-bar__label">Σ ventas</span>
        <strong class="totals-bar__value totals-bar__value--accent">
          {{ formatMoney(totalesKardex.sumVenta) }}
        </strong>
      </div>
    </div>
    </div>
  </div>
</template>

<style scoped>
.kardex-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kardex-filter {
  padding: 10px 12px;
  background: #fff;
}

.kardex-filter__field {
  max-width: 480px;
}

.kardex-summary {
  display: grid;
  grid-template-columns: minmax(180px, 1.4fr) repeat(3, minmax(120px, 1fr));
  gap: 8px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: #fff;
  min-width: 0;
}

.summary-card--product {
  background: rgba(var(--v-theme-primary), 0.03);
}

.summary-card__label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.summary-card__title {
  font-size: var(--mac-text-sm);
  font-weight: 600;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-card__value {
  font-size: 1.125rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
  color: rgb(var(--v-theme-on-surface));
}

.summary-card__value--sm {
  font-size: 0.9375rem;
}

.summary-card__meta {
  line-height: 1.3;
}

.cell-ellipsis {
  display: block;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-delta {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: rgba(var(--v-theme-on-surface), 0.6);
  white-space: nowrap;
}

.money-cell {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.kardex-table-wrap :deep(.data-table-card) {
  border-radius: var(--mac-radius) var(--mac-radius) 0 0;
}

.totals-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  gap: 1px;
  border: 1px solid var(--mac-border);
  border-top: none;
  border-radius: 0 0 var(--mac-radius) var(--mac-radius);
  overflow: hidden;
  background: rgba(var(--v-theme-primary), 0.04);
}

.totals-bar__cell {
  flex: 1 1 100px;
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 8px 12px;
  background: #fff;
  min-width: 0;
}

.totals-bar__label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.totals-bar__value {
  font-size: var(--mac-text-sm);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: rgb(var(--v-theme-on-surface));
  white-space: nowrap;
}

.totals-bar__value--accent {
  color: rgb(var(--v-theme-primary));
}

@media (max-width: 960px) {
  .kardex-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-card--product {
    grid-column: 1 / -1;
  }
}

@media (max-width: 600px) {
  .kardex-filter__field {
    max-width: 100%;
  }

  .kardex-summary {
    grid-template-columns: 1fr;
  }

  .cell-ellipsis {
    max-width: 100px;
  }
}
</style>
