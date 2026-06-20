<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { api, getErrorMessage } from '@/services/api'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { useAppStore } from '@/stores/app.store'
import { formatInteger, formatMoney } from '@/utils/format'
import type { Producto } from '@/types/catalogos.types'
import type { Existencia } from '@/types/inventario.types'

interface ExistenciaRow extends Existencia {
  almacen_nombre: string
}

const appStore = useAppStore()

const productos = ref<Producto[]>([])
const almacenes = ref<{ id: number; nombre: string }[]>([])
const selectedProducto = ref<number | null>(null)
const consolidado = ref<{ producto_id: number; cantidad_total: number; almacenes: number } | null>(null)
const existencias = ref<Existencia[]>([])
const loading = ref(false)
const search = ref('')

const productoSeleccionado = computed(() =>
  productos.value.find((p) => p.id === selectedProducto.value) ?? null,
)

const almacenMap = computed(() => Object.fromEntries(almacenes.value.map((a) => [a.id, a.nombre])))

const tableRows = computed<ExistenciaRow[]>(() =>
  existencias.value.map((e) => ({
    ...e,
    almacen_nombre: almacenMap.value[e.almacen_id] ?? `Almacén ${e.almacen_id}`,
  })),
)

const resumenPrecios = computed(() => {
  const producto = productoSeleccionado.value
  if (!producto || !consolidado.value) return null
  const stock = Math.trunc(consolidado.value.cantidad_total)
  const costo = producto.precio_base ?? null
  const venta = producto.precio_actual ?? null
  return {
    valorCosto: costo != null ? stock * costo : null,
    valorVenta: venta != null ? stock * venta : null,
  }
})

const headers = [
  { title: 'Almacén', key: 'almacen_nombre' },
  { title: 'Cant.', key: 'cantidad_actual', align: 'end' as const, width: 80 },
  { title: 'Mín.', key: 'stock_minimo', align: 'end' as const, width: 72 },
  { title: 'Máx.', key: 'stock_maximo', align: 'end' as const, width: 72 },
]

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

async function consultar() {
  if (!selectedProducto.value) {
    consolidado.value = null
    existencias.value = []
    return
  }

  loading.value = true
  try {
    const [consolidadoRes, existenciasRes] = await Promise.all([
      api.get(`/inventario/stock/consolidado/producto/${selectedProducto.value}`),
      inventarioService.getExistenciasByProducto(selectedProducto.value),
    ])
    consolidado.value = consolidadoRes.data
    existencias.value = existenciasRes.data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

watch(selectedProducto, consultar)

onMounted(loadCatalogos)
</script>

<template>
  <div class="reporte-page">
    <PageHeader
      title="Stock consolidado"
      subtitle="Saldo total por producto en todos los almacenes"
      icon="mdi-layers-outline"
    >
      <template #actions>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="loading"
          :disabled="!selectedProducto"
          @click="consultar"
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
            <template #subtitle>{{ item.raw.codigo }}</template>
          </v-list-item>
        </template>
      </v-autocomplete>
    </v-card>

    <div v-if="productoSeleccionado && consolidado" class="reporte-summary reporte-summary--4">
      <div class="summary-card summary-card--product">
        <span class="summary-card__label">Producto</span>
        <span class="summary-card__title">{{ productoSeleccionado.nombre }}</span>
        <span class="summary-card__meta text-caption text-medium-emphasis">{{ productoSeleccionado.codigo }}</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Stock total</span>
        <span class="summary-card__value">{{ formatInteger(consolidado.cantidad_total) }}</span>
        <span class="summary-card__meta">{{ consolidado.almacenes }} almacén(es)</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Inv. costo</span>
        <span class="summary-card__value summary-card__value--sm">{{ formatMoney(resumenPrecios?.valorCosto) }}</span>
        <span class="summary-card__meta">Costo: {{ formatMoney(productoSeleccionado.precio_base) }}</span>
      </div>

      <div class="summary-card">
        <span class="summary-card__label">Inv. venta</span>
        <span class="summary-card__value summary-card__value--sm">{{ formatMoney(resumenPrecios?.valorVenta) }}</span>
        <span class="summary-card__meta">P. venta: {{ formatMoney(productoSeleccionado.precio_actual) }}</span>
      </div>
    </div>

    <div class="reporte-table-wrap">
      <BaseDataTable
        v-model:search="search"
        :items="tableRows as unknown as Record<string, unknown>[]"
        :headers="headers"
        :loading="loading"
        :show-search="!!selectedProducto"
        title="Desglose por almacén"
        :subtitle="productoSeleccionado ? `Stock de ${productoSeleccionado.nombre}` : 'Selecciona un producto'"
        search-label="Buscar almacén..."
        empty-title="Selecciona un producto"
        empty-subtitle="Elige un producto para ver su stock consolidado."
      >
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
      </BaseDataTable>

      <div v-if="selectedProducto && existencias.length" class="totals-bar">
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Almacenes</span>
          <strong class="totals-bar__value">{{ existencias.length }}</strong>
        </div>
        <div class="totals-bar__cell">
          <span class="totals-bar__label">Σ unidades</span>
          <strong class="totals-bar__value totals-bar__value--accent">
            {{ formatInteger(consolidado?.cantidad_total) }}
          </strong>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '@/styles/reportes-shared.css';
</style>
