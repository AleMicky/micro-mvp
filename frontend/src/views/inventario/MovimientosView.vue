<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen, MovimientoInventario } from '@/types/inventario.types'

const appStore = useAppStore()

const items = ref<MovimientoInventario[]>([])
const productos = ref<Producto[]>([])
const almacenes = ref<Almacen[]>([])
const loading = ref(false)
const search = ref('')

const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))
const almacenMap = computed(() => Object.fromEntries(almacenes.value.map((a) => [a.id, a.nombre])))

const headers = [
  { title: 'Tipo', key: 'tipo' },
  { title: 'Producto', key: 'producto_id' },
  { title: 'Almacén', key: 'almacen_id' },
  { title: 'Cantidad', key: 'cantidad' },
  { title: 'Anterior', key: 'cantidad_anterior' },
  { title: 'Nueva', key: 'cantidad_nueva' },
  { title: 'Observaciones', key: 'observaciones' },
  { title: 'Fecha', key: 'creado_en' },
]

const tipoColors: Record<string, string> = {
  INGRESO: 'success',
  SALIDA: 'error',
  AJUSTE_POSITIVO: 'info',
  AJUSTE_NEGATIVO: 'warning',
  TRANSFERENCIA_SALIDA: 'secondary',
  TRANSFERENCIA_ENTRADA: 'primary',
}

async function loadData() {
  loading.value = true
  try {
    const [movimientosRes, productosRes, almacenesRes] = await Promise.all([
      inventarioService.getMovimientos(),
      catalogosService.getProductos(),
      inventarioService.getAlmacenes(),
    ])
    items.value = movimientosRes.data
    productos.value = productosRes.data
    almacenes.value = almacenesRes.data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <BaseDataTable
    v-model:search="search"
    :items="items"
    :headers="headers"
    :loading="loading"
    title="Movimientos de inventario"
    subtitle="Historial de movimientos registrados"
  >
    <template #item.tipo="{ value }">
      <v-chip :color="tipoColors[value] ?? 'default'" size="small" variant="tonal">
        {{ value }}
      </v-chip>
    </template>

    <template #item.producto_id="{ value }">
      {{ productoMap[value] ?? value }}
    </template>

    <template #item.almacen_id="{ value }">
      {{ almacenMap[value] ?? value }}
    </template>

    <template #item.observaciones="{ value }">
      {{ value || '—' }}
    </template>

    <template #item.creado_en="{ value }">
      {{ new Date(value).toLocaleString('es-MX') }}
    </template>
  </BaseDataTable>
</template>
