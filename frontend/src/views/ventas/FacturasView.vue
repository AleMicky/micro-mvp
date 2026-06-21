<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { ventasService } from '@/services/ventas.service'
import { catalogosService } from '@/services/catalogos.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { formatMoney } from '@/utils/format'
import { generarFacturaPdf } from '@/utils/pdf'
import { ESTADO_VENTA_COLORS, type Cliente, type Factura, type Venta } from '@/types/ventas.types'
import type { Producto } from '@/types/catalogos.types'

const appStore = useAppStore()
const items = ref<Factura[]>([])
const ventas = ref<Venta[]>([])
const clientes = ref<Cliente[]>([])
const productos = ref<Producto[]>([])
const loading = ref(false)
const search = ref('')
const detalleDialog = ref(false)
const detalleFactura = ref<Factura | null>(null)

const headers = [
  { title: 'Código', key: 'codigo' }, { title: 'Venta', key: 'venta_id' },
  { title: 'Subtotal', key: 'subtotal' }, { title: 'Total', key: 'total' },
  { title: 'Estado', key: 'estado' }, { title: 'Fecha', key: 'fecha' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 120 },
]

const ventaMap = computed(() => Object.fromEntries(ventas.value.map((v) => [v.id, v])))
const ventaCodigoMap = computed(() => Object.fromEntries(ventas.value.map((v) => [v.id, v.codigo])))
const clienteMap = computed(() => Object.fromEntries(clientes.value.map((c) => [c.id, c])))
const productoNombreMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))

async function loadData() {
  loading.value = true
  try {
    const [facturasRes, ventasRes, clientesRes, productosRes] = await Promise.all([
      ventasService.getFacturas(),
      ventasService.getVentas(),
      ventasService.getClientes(),
      catalogosService.getProductos(),
    ])
    items.value = facturasRes.data
    ventas.value = ventasRes.data
    clientes.value = clientesRes.data
    productos.value = productosRes.data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

function verDetalle(item: Factura) {
  detalleFactura.value = item
  detalleDialog.value = true
}

function descargarPdf(item: Factura) {
  try {
    const venta = ventaMap.value[item.venta_id] ?? null
    generarFacturaPdf({
      factura: item,
      venta,
      cliente: venta ? clienteMap.value[venta.cliente_id] ?? null : null,
      productoNombre: (productoId) => (productoId != null ? productoNombreMap.value[productoId] ?? `Producto #${productoId}` : '—'),
    })
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  }
}

onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Facturas" subtitle="Facturación de ventas">
    <template #item.venta_id="{ value }">{{ ventaCodigoMap[value] ?? value }}</template>
    <template #item.subtotal="{ value }">{{ formatMoney(value) }}</template>
    <template #item.total="{ value }">{{ formatMoney(value) }}</template>
    <template #item.estado="{ value }"><v-chip :color="ESTADO_VENTA_COLORS[value] ?? 'success'" size="small" variant="tonal">{{ value }}</v-chip></template>
    <template #item.actions="{ item }">
      <v-btn icon="mdi-eye-outline" size="small" variant="text" @click="verDetalle(item)" />
      <v-btn icon="mdi-file-pdf-box" size="small" variant="text" color="error" title="Descargar PDF" @click="descargarPdf(item)" />
    </template>
  </BaseDataTable>

  <v-dialog v-model="detalleDialog" max-width="640" scrollable>
    <v-card v-if="detalleFactura">
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-receipt-text-outline" />
        Factura {{ detalleFactura.codigo }}
      </v-card-title>
      <v-card-subtitle>Venta {{ ventaCodigoMap[detalleFactura.venta_id] ?? detalleFactura.venta_id }}</v-card-subtitle>
      <v-divider class="mt-2" />
      <v-card-text class="pa-5">
        <v-table density="compact">
          <thead>
            <tr>
              <th>Producto</th>
              <th class="text-right">Cantidad</th>
              <th class="text-right">Precio unitario</th>
              <th class="text-right">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(det, index) in detalleFactura.detalles" :key="index">
              <td>{{ productoNombreMap[det.producto_id ?? -1] ?? det.producto_id }}</td>
              <td class="text-right">{{ det.cantidad }}</td>
              <td class="text-right">{{ formatMoney(det.precio_unitario) }}</td>
              <td class="text-right">{{ formatMoney(det.subtotal) }}</td>
            </tr>
          </tbody>
        </v-table>

        <v-divider class="my-3" />

        <div class="d-flex justify-end ga-6">
          <div class="text-body-2">
            <div class="text-medium-emphasis">Subtotal</div>
            <div class="text-medium-emphasis">Impuesto</div>
            <div class="text-h6 font-weight-bold mt-1">Total</div>
          </div>
          <div class="text-body-2 text-right">
            <div>{{ formatMoney(detalleFactura.subtotal) }}</div>
            <div>{{ formatMoney(detalleFactura.impuesto) }}</div>
            <div class="text-h6 font-weight-bold mt-1">{{ formatMoney(detalleFactura.total) }}</div>
          </div>
        </div>
      </v-card-text>
      <v-divider />
      <v-card-actions class="pa-4">
        <v-btn color="error" variant="tonal" prepend-icon="mdi-file-pdf-box" @click="descargarPdf(detalleFactura)">Descargar PDF</v-btn>
        <v-spacer />
        <v-btn variant="text" @click="detalleDialog = false">Cerrar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
