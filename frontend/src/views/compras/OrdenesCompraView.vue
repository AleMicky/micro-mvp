<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { catalogosService } from '@/services/catalogos.service'
import { comprasService } from '@/services/compras.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { formatMoney } from '@/utils/format'
import { nonNegativeRule, positiveNumberRule, requiredRule } from '@/utils/validation'
import type { Producto } from '@/types/catalogos.types'
import { ESTADO_COMPRA_COLORS, type OrdenCompra, type OrdenCompraCreate, type Proveedor } from '@/types/compras.types'

interface DetalleRow {
  key: number
  producto_id: number | null
  cantidad: number | null
  precio_unitario: number | null
}

const appStore = useAppStore()
const items = ref<OrdenCompra[]>([])
const proveedores = ref<Proveedor[]>([])
const productos = ref<Producto[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const detailDialog = ref(false)
const confirmOpen = ref(false)
const confirmAction = ref<'delete' | 'cancel' | null>(null)
const saving = ref(false)
const acting = ref(false)
const editingId = ref<number | null>(null)
const actionTarget = ref<OrdenCompra | null>(null)
const detailItem = ref<OrdenCompra | null>(null)
const nextRowKey = ref(1)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = reactive({
  proveedor_id: null as number | null,
  fecha: new Date().toISOString().slice(0, 10),
  observacion: '',
})
const detalles = ref<DetalleRow[]>([{ key: 0, producto_id: null, cantidad: null, precio_unitario: null }])

const proveedorMap = computed(() => Object.fromEntries(proveedores.value.map((p) => [p.id, p.nombre])))
const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))

const totalOrden = computed(() =>
  detalles.value.reduce((acc, d) => {
    if (!d.cantidad || !d.precio_unitario) return acc
    return acc + Number(d.cantidad) * Number(d.precio_unitario)
  }, 0),
)

const headers = [
  { title: 'Número', key: 'codigo' },
  { title: 'Proveedor', key: 'proveedor_id' },
  { title: 'Fecha', key: 'fecha' },
  { title: 'Estado', key: 'estado' },
  { title: 'Total', key: 'total', align: 'end' as const },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 220 },
]

function productosDisponibles(currentId: number | null) {
  const used = new Set(detalles.value.map((d) => d.producto_id).filter((id) => id !== null && id !== currentId))
  return productos.value.filter((p) => !used.has(p.id))
}

function lineSubtotal(row: DetalleRow) {
  if (!row.cantidad || !row.precio_unitario) return 0
  return Number(row.cantidad) * Number(row.precio_unitario)
}

function addLine() {
  detalles.value.push({ key: nextRowKey.value++, producto_id: null, cantidad: null, precio_unitario: null })
}

function removeLine(key: number) {
  if (detalles.value.length <= 1) return
  detalles.value = detalles.value.filter((d) => d.key !== key)
}

function resetForm() {
  form.proveedor_id = null
  form.fecha = new Date().toISOString().slice(0, 10)
  form.observacion = ''
  detalles.value = [{ key: nextRowKey.value++, producto_id: null, cantidad: null, precio_unitario: null }]
}

async function loadData() {
  loading.value = true
  try {
    const [ordRes, provRes, prodRes] = await Promise.all([
      comprasService.getOrdenesCompra(),
      comprasService.getProveedores(),
      catalogosService.getProductos(),
    ])
    items.value = ordRes.data
    proveedores.value = provRes.data.filter((p) => p.activo)
    productos.value = prodRes.data.filter((p) => p.activo)
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  resetForm()
  dialog.value = true
}

function openEdit(item: OrdenCompra) {
  if (item.estado !== 'BORRADOR') {
    appStore.showError('Solo se pueden editar órdenes en BORRADOR')
    return
  }
  editingId.value = item.id
  form.proveedor_id = item.proveedor_id
  form.fecha = item.fecha ?? new Date().toISOString().slice(0, 10)
  form.observacion = item.observacion ?? ''
  detalles.value = item.detalles.map((d) => ({
    key: nextRowKey.value++,
    producto_id: d.producto_id,
    cantidad: Number(d.cantidad),
    precio_unitario: Number(d.precio_unitario),
  }))
  dialog.value = true
}

function openDetail(item: OrdenCompra) {
  detailItem.value = item
  detailDialog.value = true
}

function openDelete(item: OrdenCompra) {
  actionTarget.value = item
  confirmAction.value = 'delete'
  confirmOpen.value = true
}

function openCancel(item: OrdenCompra) {
  actionTarget.value = item
  confirmAction.value = 'cancel'
  confirmOpen.value = true
}

async function saveItem() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid || !form.proveedor_id) return

  const lineas = detalles.value.filter((d) => d.producto_id && d.cantidad && d.precio_unitario !== null)
  if (!lineas.length) {
    appStore.showError('Agregue al menos un detalle válido')
    return
  }

  const payload: OrdenCompraCreate = {
    proveedor_id: form.proveedor_id,
    fecha: form.fecha,
    observacion: form.observacion || null,
    detalles: lineas.map((d) => ({
      producto_id: d.producto_id!,
      cantidad: d.cantidad!,
      precio_unitario: d.precio_unitario!,
    })),
  }

  saving.value = true
  try {
    if (editingId.value) {
      await comprasService.updateOrdenCompra(editingId.value, payload)
      appStore.showSuccess('Orden actualizada')
    } else {
      await comprasService.createOrdenCompra(payload)
      appStore.showSuccess('Orden creada')
    }
    dialog.value = false
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

async function aprobar(item: OrdenCompra) {
  acting.value = true
  try {
    await comprasService.aprobarOrdenCompra(item.id)
    appStore.showSuccess('Orden aprobada')
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    acting.value = false
  }
}

async function confirmActionHandler() {
  if (!actionTarget.value || !confirmAction.value) return
  acting.value = true
  try {
    if (confirmAction.value === 'delete') {
      await comprasService.deleteOrdenCompra(actionTarget.value.id)
      appStore.showSuccess('Orden eliminada')
    } else {
      await comprasService.cancelarOrdenCompra(actionTarget.value.id)
      appStore.showSuccess('Orden cancelada')
    }
    confirmOpen.value = false
    actionTarget.value = null
    confirmAction.value = null
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    acting.value = false
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
    title="Órdenes de Compra"
    subtitle="Proveedor → Orden de Compra"
  >
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nueva Orden</v-btn>
    </template>
    <template #item.proveedor_id="{ value }">{{ proveedorMap[value] ?? value }}</template>
    <template #item.total="{ value }">{{ formatMoney(value) }}</template>
    <template #item.estado="{ value }">
      <v-chip :color="ESTADO_COMPRA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip>
    </template>
    <template #item.actions="{ item }">
      <v-btn icon="mdi-eye-outline" size="small" variant="text" @click="openDetail(item)" />
      <v-btn v-if="item.estado === 'BORRADOR'" icon="mdi-pencil-outline" size="small" variant="text" @click="openEdit(item)" />
      <v-btn v-if="item.estado === 'BORRADOR'" size="small" color="primary" variant="tonal" :loading="acting" @click="aprobar(item)">Aprobar</v-btn>
      <v-btn v-if="['BORRADOR', 'APROBADA'].includes(item.estado)" icon="mdi-cancel" size="small" variant="text" color="warning" @click="openCancel(item)" />
      <v-btn v-if="item.estado === 'BORRADOR'" icon="mdi-delete-outline" size="small" variant="text" color="error" @click="openDelete(item)" />
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="900" persistent scrollable>
    <v-card>
      <v-card-title class="pa-5">{{ editingId ? 'Editar orden' : 'Nueva orden de compra' }}</v-card-title>
      <v-card-text class="pa-5">
        <v-form ref="formRef">
          <v-row>
            <v-col cols="12" md="6">
              <v-select
                v-model="form.proveedor_id"
                :items="proveedores"
                item-title="nombre"
                item-value="id"
                label="Proveedor"
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.fecha" label="Fecha" type="date" :rules="[requiredRule]" />
            </v-col>
            <v-col cols="12">
              <v-textarea v-model="form.observacion" label="Observación" rows="2" />
            </v-col>
          </v-row>

          <div class="text-subtitle-2 mb-2">Detalles</div>
          <v-alert v-if="!productos.length" type="warning" variant="tonal" class="mb-3">No hay productos activos en catálogos.</v-alert>
          <div v-for="row in detalles" :key="row.key" class="mb-3">
            <v-row dense align="center">
              <v-col cols="12" md="5">
                <v-select
                  v-model="row.producto_id"
                  :items="productosDisponibles(row.producto_id)"
                  item-title="nombre"
                  item-value="id"
                  label="Producto"
                  :rules="[requiredRule]"
                />
              </v-col>
              <v-col cols="6" md="2">
                <v-text-field v-model.number="row.cantidad" label="Cantidad" type="number" :rules="[requiredRule, positiveNumberRule]" />
              </v-col>
              <v-col cols="6" md="2">
                <v-text-field v-model.number="row.precio_unitario" label="Costo unit." type="number" :rules="[requiredRule, nonNegativeRule]" />
              </v-col>
              <v-col cols="8" md="2" class="text-end text-body-2">{{ formatMoney(lineSubtotal(row)) }}</v-col>
              <v-col cols="4" md="1" class="text-end">
                <v-btn icon="mdi-delete-outline" size="small" variant="text" color="error" :disabled="detalles.length <= 1" @click="removeLine(row.key)" />
              </v-col>
            </v-row>
          </div>
          <v-btn variant="tonal" prepend-icon="mdi-plus" @click="addLine">Agregar línea</v-btn>
          <div class="text-h6 text-end mt-4">Total: {{ formatMoney(totalOrden) }}</div>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-5">
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
        <v-btn color="primary" :loading="saving" @click="saveItem">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="detailDialog" max-width="720">
    <v-card v-if="detailItem">
      <v-card-title class="pa-5">Orden {{ detailItem.codigo }}</v-card-title>
      <v-card-text class="pa-5">
        <v-row dense>
          <v-col cols="6"><strong>Proveedor:</strong> {{ proveedorMap[detailItem.proveedor_id] }}</v-col>
          <v-col cols="6"><strong>Estado:</strong> {{ detailItem.estado }}</v-col>
          <v-col cols="6"><strong>Fecha:</strong> {{ detailItem.fecha }}</v-col>
          <v-col cols="6"><strong>Total:</strong> {{ formatMoney(detailItem.total) }}</v-col>
        </v-row>
        <v-table density="compact" class="mt-4">
          <thead><tr><th>Producto</th><th>Cant.</th><th>Costo</th><th>Subtotal</th></tr></thead>
          <tbody>
            <tr v-for="d in detailItem.detalles" :key="d.id">
              <td>{{ d.producto_nombre ?? productoMap[d.producto_id] ?? d.producto_id }}</td>
              <td>{{ d.cantidad }}</td>
              <td>{{ formatMoney(d.precio_unitario) }}</td>
              <td>{{ formatMoney(d.subtotal ?? Number(d.cantidad) * Number(d.precio_unitario)) }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
      <v-card-actions class="pa-5"><v-spacer /><v-btn variant="text" @click="detailDialog = false">Cerrar</v-btn></v-card-actions>
    </v-card>
  </v-dialog>

  <ConfirmDialog
    v-model="confirmOpen"
    :loading="acting"
    :message="confirmAction === 'delete' ? `¿Eliminar orden ${actionTarget?.codigo}?` : `¿Cancelar orden ${actionTarget?.codigo}?`"
    @confirm="confirmActionHandler"
  />
</template>
