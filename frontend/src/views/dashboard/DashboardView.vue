<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { comprasService } from '@/services/compras.service'
import { ventasService } from '@/services/ventas.service'
import { finanzasService } from '@/services/finanzas.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import MovimientosInventarioTable from '@/components/MovimientosInventarioTable.vue'
import { enrichMovimiento } from '@/utils/inventario-movimientos'
import type { Existencia, MovimientoInventario } from '@/types/inventario.types'
import type { OrdenCompra } from '@/types/compras.types'

const appStore = useAppStore()
const loading = ref(true)
const totalProductos = ref(0)
const totalAlmacenes = ref(0)
const stockBajo = ref(0)
const comprasPendientes = ref(0)
const ventasMes = ref(0)
const totalCxc = ref(0)
const totalCxp = ref(0)
const movimientosRecientes = ref<MovimientoInventario[]>([])
const productoMap = ref<Record<number, { nombre: string; codigo?: string }>>({})
const almacenMap = ref<Record<number, string>>({})

const movimientosRows = computed(() =>
  movimientosRecientes.value.map((m) => enrichMovimiento(m, productoMap.value, almacenMap.value)),
)

const stats = computed(() => [
  { title: 'Productos', value: totalProductos.value, icon: 'mdi-package-variant-closed', color: 'primary', hint: 'En catálogo' },
  { title: 'Almacenes', value: totalAlmacenes.value, icon: 'mdi-warehouse', color: 'info', hint: 'Activos' },
  { title: 'Stock bajo', value: stockBajo.value, icon: 'mdi-alert-circle-outline', color: 'warning', hint: 'Requieren atención' },
  { title: 'Compras pendientes', value: comprasPendientes.value, icon: 'mdi-cart-arrow-down', color: 'secondary', hint: 'OC por aprobar/recibir' },
  { title: 'Ventas del mes', value: ventasMes.value, icon: 'mdi-cart-arrow-up', color: 'success', hint: 'Ventas registradas' },
  { title: 'Cuentas por cobrar', value: totalCxc.value, icon: 'mdi-cash-plus', color: 'teal', hint: 'Saldo pendiente' },
  { title: 'Cuentas por pagar', value: totalCxp.value, icon: 'mdi-cash-minus', color: 'error', hint: 'Saldo pendiente' },
  { title: 'Movimientos', value: movimientosRecientes.value.length, icon: 'mdi-swap-horizontal', color: 'primary', hint: 'Recientes' },
])

function countStockBajo(existencias: Existencia[]) {
  return existencias.filter((e) => Number(e.cantidad_actual) <= Number(e.stock_minimo) && Number(e.stock_minimo) > 0).length
}

function sumSaldo(items: { saldo: number | string }[]) {
  return items.reduce((acc, i) => acc + Number(i.saldo), 0)
}

async function loadDashboard() {
  loading.value = true
  try {
    const [productosRes, almacenesRes, existenciasRes, movimientosRes, ordenesRes, ventasRes, cxcRes, cxpRes] = await Promise.all([
      catalogosService.getProductos(),
      inventarioService.getAlmacenes(),
      inventarioService.getExistencias(),
      inventarioService.getMovimientos({ limit: 500 }),
      comprasService.getOrdenes(),
      ventasService.getVentas(),
      finanzasService.getCuentasPorCobrar(),
      finanzasService.getCuentasPorPagar(),
    ])

    totalProductos.value = productosRes.data.length
    totalAlmacenes.value = almacenesRes.data.length
    productoMap.value = Object.fromEntries(
      productosRes.data.map((p) => [p.id, { nombre: p.nombre, codigo: p.codigo }]),
    )
    almacenMap.value = Object.fromEntries(almacenesRes.data.map((a) => [a.id, a.nombre]))
    stockBajo.value = countStockBajo(existenciasRes.data)
    comprasPendientes.value = ordenesRes.data.filter((o: OrdenCompra) => ['PENDIENTE', 'APROBADA'].includes(o.estado)).length
    ventasMes.value = ventasRes.data.length
    totalCxc.value = Math.round(sumSaldo(cxcRes.data))
    totalCxp.value = Math.round(sumSaldo(cxpRes.data))
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
  <div class="dashboard-page">
    <PageHeader title="Dashboard" subtitle="Resumen general del sistema" icon="mdi-view-dashboard-outline" />

    <v-container fluid class="px-0">
      <v-row class="mx-0">
        <v-col v-for="stat in stats" :key="stat.title" cols="12" sm="6" lg="3" class="px-1 pb-2">
          <v-card class="stat-card pa-3" :loading="loading">
          <div class="d-flex justify-space-between align-start">
            <div>
              <div class="text-caption text-medium-emphasis mb-0">{{ stat.title }}</div>
              <div class="text-h5 font-weight-bold">{{ stat.value }}</div>
              <div class="text-caption text-medium-emphasis mt-1">{{ stat.hint }}</div>
            </div>
            <v-avatar :color="stat.color" variant="tonal" size="36" rounded="md">
              <v-icon :icon="stat.icon" size="18" />
            </v-avatar>
          </div>
        </v-card>
      </v-col>
      </v-row>

      <MovimientosInventarioTable
        :items="movimientosRows"
        :loading="loading"
        title="Movimientos recientes de inventario"
        subtitle="Recepciones, ingresos, salidas, ajustes y transferencias"
        :show-search="false"
        compact
      />
    </v-container>
  </div>
</template>

<style scoped>
.dashboard-page {
  width: calc(100% + 28px);
  margin: 0 -14px;
}

@media (min-width: 960px) {
  .dashboard-page {
    width: calc(100% + 40px);
    margin: 0 -20px;
  }
}
</style>
