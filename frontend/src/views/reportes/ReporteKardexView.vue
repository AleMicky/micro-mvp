<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import MovimientosInventarioTable from '@/components/MovimientosInventarioTable.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { reportesService } from '@/services/reportes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { enrichMovimiento, isMovimientoEntrada } from '@/utils/inventario-movimientos'
import { formatInteger, formatMoney } from '@/utils/format'
import type { Producto } from '@/types/catalogos.types'
import type { Existencia, MovimientoInventario, TipoMovimiento } from '@/types/inventario.types'

const appStore = useAppStore()

const productos = ref<Producto[]>([])
const almacenes = ref<{ id: number; nombre: string }[]>([])
const selectedProducto = ref<number | null>(null)
const movimientos = ref<MovimientoInventario[]>([])
const existencias = ref<Existencia[]>([])
const totalRegistros = ref(0)
const loading = ref(false)
const search = ref('')

const productoSeleccionado = computed(() =>
  productos.value.find((p) => p.id === selectedProducto.value) ?? null,
)

const productoMap = computed(() =>
  Object.fromEntries(productos.value.map((p) => [p.id, { nombre: p.nombre, codigo: p.codigo }])),
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
  const base = movimientos.value.map((m) =>
    enrichMovimiento(m, productoMap.value, almacenMap.value),
  )
  if (!term) return base
  return base.filter((m) => {
    const texto = [
      m.tipo,
      m.almacen_nombre,
      m.referencia_label,
      m.observaciones,
      formatInteger(m.cantidad),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return texto.includes(term)
  })
})

const resumenMovimientos = computed(() => {
  let entradas = 0
  let salidas = 0
  let sumCantidad = 0

  for (const m of movimientosVisibles.value) {
    const qty = Number(m.cantidad)
    if (Number.isFinite(qty)) sumCantidad += qty
    if (isMovimientoEntrada(m.tipo as TipoMovimiento)) entradas++
    else if (m.tipo === 'SALIDA' || m.tipo === 'AJUSTE_NEGATIVO' || m.tipo === 'TRANSFERENCIA_SALIDA') salidas++
  }

  return {
    filas: movimientosVisibles.value.length,
    entradas,
    salidas,
    sumCantidad: Math.trunc(sumCantidad),
  }
})

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

async function loadReporte() {
  if (!selectedProducto.value) {
    movimientos.value = []
    existencias.value = []
    totalRegistros.value = 0
    return
  }

  loading.value = true
  try {
    const [reporteRes, existenciasRes] = await Promise.all([
      reportesService.getKardex(selectedProducto.value),
      inventarioService.getExistenciasByProducto(selectedProducto.value),
    ])
    const data = reporteRes.data as { items?: MovimientoInventario[]; total?: number }
    movimientos.value = data.items ?? []
    totalRegistros.value = data.total ?? movimientos.value.length
    existencias.value = existenciasRes.data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

watch(selectedProducto, loadReporte)

onMounted(loadCatalogos)
</script>

<template>
  <div class="reporte-page">
    <PageHeader
      title="Reporte de kardex"
      subtitle="Movimientos de inventario por producto"
      icon="mdi-file-document-outline"
    >
      <template #actions>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="loading"
          :disabled="!selectedProducto"
          @click="loadReporte"
        >
          Actualizar
        </v-btn>
      </template>
    </PageHeader>

    <v-card class="reporte-filter" border elevation="0">
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
        placeholder="Seleccionar producto..."
        class="reporte-filter__field reporte-filter__field--wide"
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

    <div v-if="productoSeleccionado" class="reporte-summary">
      <div class="summary-card summary-card--product">
        <span class="summary-card__label">Producto</span>
        <span class="summary-card__title">{{ productoSeleccionado.nombre }}</span>
        <span class="summary-card__meta text-caption text-medium-emphasis">{{ productoSeleccionado.codigo }}</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Stock actual</span>
        <span class="summary-card__value">{{ formatInteger(stockTotal) }}</span>
        <span class="summary-card__meta">{{ totalRegistros }} movimiento(s)</span>
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

    <div class="reporte-table-wrap">
      <MovimientosInventarioTable
        v-model:search="search"
        :items="movimientosVisibles"
        :loading="loading"
        compact
        :show-producto="false"
        :show-search="!!selectedProducto"
        title="Detalle de movimientos"
        :subtitle="productoSeleccionado ? `Kardex de ${productoSeleccionado.nombre}` : 'Selecciona un producto'"
        search-label="Filtrar movimiento..."
        empty-title="Selecciona un producto"
        empty-subtitle="Elige un producto para generar el reporte de kardex."
        @refresh="loadReporte"
      />

      <div v-if="selectedProducto && movimientos.length" class="totals-bar">
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Registros</span>
          <strong class="totals-bar__value">{{ resumenMovimientos.filas }}</strong>
        </div>
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Entradas</span>
          <strong class="totals-bar__value text-success">{{ resumenMovimientos.entradas }}</strong>
        </div>
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Salidas</span>
          <strong class="totals-bar__value text-error">{{ resumenMovimientos.salidas }}</strong>
        </div>
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Σ cantidad</span>
          <strong class="totals-bar__value">{{ formatInteger(resumenMovimientos.sumCantidad) }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@/styles/reportes-shared.css';
</style>
