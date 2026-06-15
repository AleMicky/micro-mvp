<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Existencia, MovimientoInventario } from '@/types/inventario.types'

const appStore = useAppStore()

const loading = ref(true)
const totalProductos = ref(0)
const totalAlmacenes = ref(0)
const stockBajo = ref(0)
const movimientosRecientes = ref<MovimientoInventario[]>([])

const stats = computed(() => [
  {
    title: 'Productos',
    value: totalProductos.value,
    icon: 'mdi-package-variant-closed',
    color: 'primary',
    hint: 'En catálogo',
  },
  {
    title: 'Almacenes',
    value: totalAlmacenes.value,
    icon: 'mdi-warehouse',
    color: 'info',
    hint: 'Activos',
  },
  {
    title: 'Stock bajo',
    value: stockBajo.value,
    icon: 'mdi-alert-circle-outline',
    color: 'warning',
    hint: 'Requieren atención',
  },
  {
    title: 'Movimientos',
    value: movimientosRecientes.value.length,
    icon: 'mdi-swap-horizontal',
    color: 'success',
    hint: 'Recientes',
  },
])

const movimientoHeaders = [
  { title: 'Tipo', key: 'tipo' },
  { title: 'Producto', key: 'producto_id' },
  { title: 'Almacén', key: 'almacen_id' },
  { title: 'Cantidad', key: 'cantidad' },
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

function countStockBajo(existencias: Existencia[]) {
  return existencias.filter(
    (e) => Number(e.cantidad_actual) <= Number(e.stock_minimo) && Number(e.stock_minimo) > 0,
  ).length
}

async function loadDashboard() {
  loading.value = true
  try {
    const [productosRes, almacenesRes, existenciasRes, movimientosRes] = await Promise.all([
      catalogosService.getProductos(),
      inventarioService.getAlmacenes(),
      inventarioService.getExistencias(),
      inventarioService.getMovimientos(),
    ])

    totalProductos.value = productosRes.data.length
    totalAlmacenes.value = almacenesRes.data.length
    stockBajo.value = countStockBajo(existenciasRes.data)
    movimientosRecientes.value = movimientosRes.data.slice(0, 8)
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div>
    <PageHeader
      title="Dashboard"
      subtitle="Resumen general de catálogos e inventario"
      icon="mdi-view-dashboard-outline"
    />

    <v-row>
      <v-col v-for="stat in stats" :key="stat.title" cols="12" sm="6" lg="3">
        <v-card class="stat-card pa-5" :loading="loading">
          <div class="d-flex justify-space-between align-start">
            <div>
              <div class="text-caption text-medium-emphasis mb-1">{{ stat.title }}</div>
              <div class="text-h3 font-weight-bold">{{ stat.value }}</div>
              <div class="text-caption text-medium-emphasis mt-2">{{ stat.hint }}</div>
            </div>
            <v-avatar :color="stat.color" variant="tonal" size="52" rounded="lg">
              <v-icon :icon="stat.icon" size="26" />
            </v-avatar>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="mt-6" border elevation="0">
      <v-card-title class="pa-5 pb-2">
        <div class="text-h6 font-weight-bold">Movimientos recientes</div>
        <div class="text-body-2 text-medium-emphasis">Últimas operaciones registradas</div>
      </v-card-title>
      <v-card-text class="pa-5 pt-0">
        <v-data-table
          :headers="movimientoHeaders"
          :items="movimientosRecientes"
          :loading="loading"
          item-value="id"
          hover
          class="rounded-lg"
          :items-per-page="8"
          hide-default-footer
        >
          <template #item.tipo="{ value }">
            <v-chip :color="tipoColors[value] ?? 'default'" size="small" variant="tonal">
              {{ value }}
            </v-chip>
          </template>
          <template #item.creado_en="{ value }">
            {{ new Date(value).toLocaleString('es-MX') }}
          </template>
          <template #no-data>
            <div class="text-center py-8 text-medium-emphasis">No hay movimientos recientes</div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>
