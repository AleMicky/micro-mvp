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

const movimientoHeaders = [
  { title: 'Tipo', key: 'tipo' },
  { title: 'Producto', key: 'producto_id' },
  { title: 'Almacén', key: 'almacen_id' },
  { title: 'Cantidad', key: 'cantidad' },
  { title: 'Fecha', key: 'creado_en' },
]

const tipoColors: Record<string, string> = {
  INGRESO: 'success', SALIDA: 'error', AJUSTE_POSITIVO: 'info', AJUSTE_NEGATIVO: 'warning',
  TRANSFERENCIA_SALIDA: 'secondary', TRANSFERENCIA_ENTRADA: 'primary',
}

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
      inventarioService.getMovimientos(),
      comprasService.getOrdenes(),
      ventasService.getVentas(),
      finanzasService.getCuentasPorCobrar(),
      finanzasService.getCuentasPorPagar(),
    ])

    totalProductos.value = productosRes.data.length
    totalAlmacenes.value = almacenesRes.data.length
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
  <div>
    <PageHeader title="Dashboard" subtitle="Resumen general del sistema" icon="mdi-view-dashboard-outline" />

    <v-row>
      <v-col v-for="stat in stats" :key="stat.title" cols="12" sm="6" lg="3">
        <v-card class="stat-card pa-5" :loading="loading">
          <div class="d-flex justify-space-between align-start">
            <div>
              <div class="text-caption text-medium-emphasis mb-1">{{ stat.title }}</div>
              <div class="text-h4 font-weight-bold">{{ stat.value }}</div>
              <div class="text-caption text-medium-emphasis mt-2">{{ stat.hint }}</div>
            </div>
            <v-avatar :color="stat.color" variant="tonal" size="48" rounded="lg">
              <v-icon :icon="stat.icon" size="24" />
            </v-avatar>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="mt-6" border elevation="0">
      <v-card-title class="pa-5 pb-2">
        <div class="text-h6 font-weight-bold">Movimientos recientes</div>
      </v-card-title>
      <v-card-text class="pa-5 pt-0">
        <v-data-table :headers="movimientoHeaders" :items="movimientosRecientes" :loading="loading" item-value="id" hover :items-per-page="8" hide-default-footer>
          <template #item.tipo="{ value }">
            <v-chip :color="tipoColors[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip>
          </template>
          <template #item.creado_en="{ value }">{{ new Date(value).toLocaleString('es-MX') }}</template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>
