<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Producto } from '@/types/catalogos.types'
import type { MovimientoInventario } from '@/types/inventario.types'

const appStore = useAppStore()

const productos = ref<Producto[]>([])
const selectedProducto = ref<number | null>(null)
const movimientos = ref<MovimientoInventario[]>([])
const totalMovimientos = ref(0)
const loading = ref(false)
const search = ref('')

const productoNombre = computed(() =>
  productos.value.find((p) => p.id === selectedProducto.value)?.nombre ?? '',
)

const headers = [
  { title: 'Tipo', key: 'tipo' },
  { title: 'Almacén', key: 'almacen_id' },
  { title: 'Cantidad', key: 'cantidad' },
  { title: 'Anterior', key: 'cantidad_anterior' },
  { title: 'Nueva', key: 'cantidad_nueva' },
  { title: 'Observaciones', key: 'observaciones' },
  { title: 'Fecha', key: 'creado_en' },
]

async function loadProductos() {
  try {
    const { data } = await catalogosService.getProductos()
    productos.value = data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  }
}

async function loadKardex() {
  if (!selectedProducto.value) {
    movimientos.value = []
    totalMovimientos.value = 0
    return
  }
  loading.value = true
  try {
    const { data } = await inventarioService.getKardex(selectedProducto.value)
    movimientos.value = data.movimientos
    totalMovimientos.value = data.total_movimientos
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

watch(selectedProducto, loadKardex)

loadProductos()
</script>

<template>
  <div>
    <PageHeader
      title="Kardex"
      subtitle="Historial de movimientos por producto"
      icon="mdi-file-document-outline"
    />

    <v-card class="mb-4 pa-5" border elevation="0">
      <v-select
        v-model="selectedProducto"
        :items="productos"
        item-title="nombre"
        item-value="id"
        label="Seleccionar producto"
        prepend-inner-icon="mdi-package-variant-closed"
        clearable
        hide-details
      />
      <v-alert v-if="selectedProducto" type="info" variant="tonal" density="compact" class="mt-4">
        Kardex de <strong>{{ productoNombre }}</strong> — {{ totalMovimientos }} movimiento(s)
      </v-alert>
    </v-card>

    <BaseDataTable
      v-model:search="search"
      :items="movimientos"
      :headers="headers"
      :loading="loading"
      :show-search="!!selectedProducto"
      empty-title="Selecciona un producto"
      empty-subtitle="Elige un producto para ver su kardex de movimientos."
    >
      <template #item.observaciones="{ value }">
        {{ value || '—' }}
      </template>

      <template #item.creado_en="{ value }">
        {{ new Date(value).toLocaleString('es-MX') }}
      </template>
    </BaseDataTable>
  </div>
</template>
