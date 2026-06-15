<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
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

const headers = [
  { title: 'Producto', key: 'producto_id' },
  { title: 'Almacén', key: 'almacen_id' },
  { title: 'Cantidad', key: 'cantidad_actual' },
  { title: 'Mínimo', key: 'stock_minimo' },
  { title: 'Máximo', key: 'stock_maximo' },
  { title: 'Estado', key: 'stock_status' },
]

function getStockStatus(item: Existencia) {
  const actual = Number(item.cantidad_actual)
  const minimo = Number(item.stock_minimo)
  if (minimo > 0 && actual <= minimo) return 'bajo'
  return 'ok'
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
  <div>
    <PageHeader
      title="Existencias"
      subtitle="Consulta de stock por producto y almacén"
      icon="mdi-package-check"
    />

    <BaseDataTable
      v-model:search="search"
      :items="items"
      :headers="headers"
      :loading="loading"
      show-search
      empty-subtitle="Registra ingresos de stock para ver existencias."
    >
      <template #toolbar>
        <v-select
          v-model="filterProducto"
          :items="productos"
          item-title="nombre"
          item-value="id"
          label="Producto"
          clearable
          hide-details
          density="compact"
          style="min-width: 200px"
          @update:model-value="filterAlmacen = null"
        />
        <v-select
          v-model="filterAlmacen"
          :items="almacenes"
          item-title="nombre"
          item-value="id"
          label="Almacén"
          clearable
          hide-details
          density="compact"
          style="min-width: 200px"
          @update:model-value="filterProducto = null"
        />
      </template>

      <template #item.producto_id="{ value }">
        {{ productoMap[value] ?? value }}
      </template>

      <template #item.almacen_id="{ value }">
        {{ almacenMap[value] ?? value }}
      </template>

      <template #item.stock_maximo="{ value }">
        {{ value ?? '—' }}
      </template>

      <template #item.stock_status="{ item }">
        <v-chip
          :color="getStockStatus(item) === 'bajo' ? 'warning' : 'success'"
          size="small"
          variant="tonal"
        >
          {{ getStockStatus(item) === 'bajo' ? 'Stock bajo' : 'Normal' }}
        </v-chip>
      </template>
    </BaseDataTable>
  </div>
</template>
