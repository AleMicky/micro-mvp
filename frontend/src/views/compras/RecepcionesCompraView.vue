<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { catalogosService } from '@/services/catalogos.service'
import { comprasService } from '@/services/compras.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { formatMoney } from '@/utils/format'
import { nonNegativeRule, positiveNumberRule, requiredRule } from '@/utils/validation'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen } from '@/types/inventario.types'
import {
  ESTADO_COMPRA_COLORS,
  type OrdenCompra,
  type RecepcionCompra,
  type RecepcionCompraCreate,
} from '@/types/compras.types'

interface DetalleRow {
  key: number
  producto_id: number | null
  cantidad_recibida: number | null
  costo_unitario: number | null
}

const appStore = useAppStore()
const items = ref<RecepcionCompra[]>([])
const ordenes = ref<OrdenCompra[]>([])
const almacenes = ref<Almacen[]>([])
const productos = ref<Producto[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const detailDialog = ref(false)
const confirmOpen = ref(false)
const confirmAction = ref<'delete' | 'cancel' | 'confirm' | null>(null)
const saving = ref(false)
const acting = ref(false)
const editingId = ref<number | null>(null)
const actionTarget = ref<RecepcionCompra | null>(null)
const detailItem = ref<RecepcionCompra | null>(null)
const nextRowKey = ref(1)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = reactive({
  orden_compra_id: null as number | null,
  almacen_id: null as number | null,
  fecha: new Date().toISOString().slice(0, 10),
  observacion: '',
})
const detalles = ref<DetalleRow[]>([{ key: 0, producto_id: null, cantidad_recibida: null, costo_unitario: null }])

const ordenesAprobadas = computed(() => ordenes.value.filter((o) => o.estado === 'APROBADA'))
const ordenMap = computed(() => Object.fromEntries(ordenes.value.map((o) => [o.id, o.codigo])))
const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))

const totalRecepcion = computed(() =>
  detalles.value.reduce((acc, d) => {
    if (!d.cantidad_recibida || d.costo_unitario === null) return acc
    return acc + Number(d.cantidad_recibida) * Number(d.costo_unitario)
  }, 0),
)

const headers = [
  { title: 'Número', key: 'codigo' },
  { title: 'Orden', key: 'orden_compra_id' },
  { title: 'Almacén', key: 'almacen_nombre' },
  { title: 'Sucursal', key: 'sucursal_nombre' },
  { title: 'Estado', key: 'estado' },
  { title: 'Total', key: 'total', align: 'end' as const },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 240 },
]

function lineSubtotal(row: DetalleRow) {
  if (!row.cantidad_recibida || row.costo_unitario === null) return 0
  return Number(row.cantidad_recibida) * Number(row.costo_unitario)
}

function addLine() {
  detalles.value.push({ key: nextRowKey.value++, producto_id: null, cantidad_recibida: null, costo_unitario: null })
}

function removeLine(key: number) {
  if (detalles.value.length <= 1) return
  detalles.value = detalles.value.filter((d) => d.key !== key)
}

function resetForm() {
  form.orden_compra_id = null
  form.almacen_id = null
  form.fecha = new Date().toISOString().slice(0, 10)
  form.observacion = ''
  detalles.value = [{ key: nextRowKey.value++, producto_id: null, cantidad_recibida: null, costo_unitario: null }]
}

function loadDetallesFromOrden(ordenId: number | null) {
  if (!ordenId) return
  const orden = ordenes.value.find((o) => o.id === ordenId)
  if (!orden) return
  detalles.value = orden.detalles.map((d) => ({
    key: nextRowKey.value++,
    producto_id: d.producto_id,
    cantidad_recibida: Number(d.cantidad),
    costo_unitario: Number(d.precio_unitario),
  }))
}

watch(() => form.orden_compra_id, (id) => {
  if (!editingId.value && id) loadDetallesFromOrden(id)
})

async function loadData() {
  loading.value = true
  try {
    const [recRes, ordRes, almRes, prodRes] = await Promise.all([
      comprasService.getRecepcionesCompra(),
      comprasService.getOrdenesCompra(),
      inventarioService.getAlmacenes(),
      catalogosService.getProductos(),
    ])
    items.value = recRes.data
    ordenes.value = ordRes.data
    almacenes.value = almRes.data.filter((a) => a.activo)
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

function openEdit(item: RecepcionCompra) {
  if (item.estado !== 'BORRADOR') {
    appStore.showError('Solo se pueden editar recepciones en BORRADOR')
    return
  }
  editingId.value = item.id
  form.orden_compra_id = item.orden_compra_id
  form.almacen_id = item.almacen_id
  form.fecha = item.fecha ?? new Date().toISOString().slice(0, 10)
  form.observacion = item.observacion ?? ''
  detalles.value = item.detalles.map((d) => ({
    key: nextRowKey.value++,
    producto_id: d.producto_id,
    cantidad_recibida: Number(d.cantidad_recibida),
    costo_unitario: Number(d.costo_unitario),
  }))
  dialog.value = true
}

function openDetail(item: RecepcionCompra) {
  detailItem.value = item
  detailDialog.value = true
}

function openConfirm(item: RecepcionCompra) {
  actionTarget.value = item
  confirmAction.value = 'confirm'
  confirmOpen.value = true
}

function openCancel(item: RecepcionCompra) {
  actionTarget.value = item
  confirmAction.value = 'cancel'
  confirmOpen.value = true
}

function openDelete(item: RecepcionCompra) {
  actionTarget.value = item
  confirmAction.value = 'delete'
  confirmOpen.value = true
}

async function saveItem() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid || !form.orden_compra_id || !form.almacen_id) return

  const lineas = detalles.value.filter((d) => d.producto_id && d.cantidad_recibida && d.costo_unitario !== null)
  if (!lineas.length) {
    appStore.showError('Agregue al menos un detalle válido')
    return
  }

  const payload: RecepcionCompraCreate = {
    orden_compra_id: form.orden_compra_id,
    almacen_id: form.almacen_id,
    fecha: form.fecha,
    observacion: form.observacion || null,
    detalles: lineas.map((d) => ({
      producto_id: d.producto_id!,
      cantidad_recibida: d.cantidad_recibida!,
      costo_unitario: d.costo_unitario!,
    })),
  }

  saving.value = true
  try {
    if (editingId.value) {
      await comprasService.updateRecepcionCompra(editingId.value, payload)
      appStore.showSuccess('Recepción actualizada')
    } else {
      await comprasService.createRecepcionCompra(payload)
      appStore.showSuccess('Recepción creada')
    }
    dialog.value = false
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

async function confirmActionHandler() {
  if (!actionTarget.value || !confirmAction.value) return
  acting.value = true
  try {
    if (confirmAction.value === 'confirm') {
      await comprasService.confirmarRecepcionCompra(actionTarget.value.id)
      appStore.showSuccess('Recepción confirmada e inventario actualizado')
    } else if (confirmAction.value === 'cancel') {
      await comprasService.cancelarRecepcionCompra(actionTarget.value.id)
      appStore.showSuccess('Recepción cancelada')
    } else {
      await comprasService.deleteRecepcionCompra(actionTarget.value.id)
      appStore.showSuccess('Recepción eliminada')
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
    title="Recepciones de Compra"
    subtitle="Orden aprobada → Recepción → Ingreso a inventario"
  >
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nueva Recepción</v-btn>
    </template>
    <template #item.orden_compra_id="{ value }">{{ ordenMap[value] ?? value }}</template>
    <template #item.almacen_nombre="{ item }">{{ item.almacen_nombre ?? item.almacen_id }}</template>
    <template #item.total="{ value }">{{ formatMoney(value) }}</template>
    <template #item.estado="{ value }">
      <v-chip :color="ESTADO_COMPRA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip>
    </template>
    <template #item.actions="{ item }">
      <v-btn icon="mdi-eye-outline" size="small" variant="text" @click="openDetail(item)" />
      <v-btn v-if="item.estado === 'BORRADOR'" icon="mdi-pencil-outline" size="small" variant="text" @click="openEdit(item)" />
      <v-btn v-if="item.estado === 'BORRADOR'" size="small" color="success" variant="tonal" :loading="acting" @click="openConfirm(item)">Confirmar</v-btn>
      <v-btn v-if="item.estado === 'BORRADOR'" icon="mdi-cancel" size="small" variant="text" color="warning" @click="openCancel(item)" />
      <v-btn v-if="item.estado === 'BORRADOR'" icon="mdi-delete-outline" size="small" variant="text" color="error" @click="openDelete(item)" />
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="900" persistent scrollable>
    <v-card>
      <v-card-title class="pa-5">{{ editingId ? 'Editar recepción' : 'Nueva recepción de compra' }}</v-card-title>
      <v-card-text class="pa-5">
        <v-form ref="formRef">
          <v-row>
            <v-col cols="12" md="6">
              <v-select
                v-model="form.orden_compra_id"
                :items="ordenesAprobadas"
                item-title="codigo"
                item-value="id"
                label="Orden aprobada"
                :rules="[requiredRule]"
                :disabled="!!editingId"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="form.almacen_id"
                :items="almacenes"
                item-title="nombre"
                item-value="id"
                label="Almacén destino"
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

          <div class="text-subtitle-2 mb-2">Detalles recibidos</div>
          <div v-for="row in detalles" :key="row.key" class="mb-3">
            <v-row dense align="center">
              <v-col cols="12" md="5">
                <v-select
                  v-model="row.producto_id"
                  :items="productos"
                  item-title="nombre"
                  item-value="id"
                  label="Producto"
                  :rules="[requiredRule]"
                />
              </v-col>
              <v-col cols="6" md="2">
                <v-text-field v-model.number="row.cantidad_recibida" label="Cant. recibida" type="number" :rules="[requiredRule, positiveNumberRule]" />
              </v-col>
              <v-col cols="6" md="2">
                <v-text-field v-model.number="row.costo_unitario" label="Costo unit." type="number" :rules="[requiredRule, nonNegativeRule]" />
              </v-col>
              <v-col cols="8" md="2" class="text-end text-body-2">{{ formatMoney(lineSubtotal(row)) }}</v-col>
              <v-col cols="4" md="1" class="text-end">
                <v-btn icon="mdi-delete-outline" size="small" variant="text" color="error" :disabled="detalles.length <= 1" @click="removeLine(row.key)" />
              </v-col>
            </v-row>
          </div>
          <v-btn variant="tonal" prepend-icon="mdi-plus" @click="addLine">Agregar línea</v-btn>
          <div class="text-h6 text-end mt-4">Total: {{ formatMoney(totalRecepcion) }}</div>
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
      <v-card-title class="pa-5">Recepción {{ detailItem.codigo }}</v-card-title>
      <v-card-text class="pa-5">
        <v-row dense>
          <v-col cols="6"><strong>Orden:</strong> {{ ordenMap[detailItem.orden_compra_id] }}</v-col>
          <v-col cols="6"><strong>Estado:</strong> {{ detailItem.estado }}</v-col>
          <v-col cols="6"><strong>Almacén:</strong> {{ detailItem.almacen_nombre }}</v-col>
          <v-col cols="6"><strong>Sucursal:</strong> {{ detailItem.sucursal_nombre }}</v-col>
          <v-col cols="6"><strong>Total:</strong> {{ formatMoney(detailItem.total) }}</v-col>
        </v-row>
        <v-table density="compact" class="mt-4">
          <thead><tr><th>Producto</th><th>Cant. recibida</th><th>Costo</th><th>Subtotal</th></tr></thead>
          <tbody>
            <tr v-for="d in detailItem.detalles" :key="d.id">
              <td>{{ d.producto_nombre ?? productoMap[d.producto_id] ?? d.producto_id }}</td>
              <td>{{ d.cantidad_recibida }}</td>
              <td>{{ formatMoney(d.costo_unitario) }}</td>
              <td>{{ formatMoney(d.subtotal ?? Number(d.cantidad_recibida) * Number(d.costo_unitario)) }}</td>
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
    :message="
      confirmAction === 'confirm'
        ? `¿Confirmar recepción ${actionTarget?.codigo}? Se registrará ingreso en inventario.`
        : confirmAction === 'cancel'
          ? `¿Cancelar recepción ${actionTarget?.codigo}?`
          : `¿Eliminar recepción ${actionTarget?.codigo}?`
    "
    @confirm="confirmActionHandler"
  />
</template>
