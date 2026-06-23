<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { ventasService } from '@/services/ventas.service'
import { catalogosService } from '@/services/catalogos.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { integerRule, requiredRule } from '@/utils/validation'
import { ESTADO_VENTA_COLORS, type Cliente, type CotizacionVenta, type DetalleVenta } from '@/types/ventas.types'
import type { Producto } from '@/types/catalogos.types'

const appStore = useAppStore()
const items = ref<CotizacionVenta[]>([])
const clientes = ref<Cliente[]>([])
const productos = ref<Producto[]>([])
const loading = ref(false)
const loadingCatalogos = ref(false)
const saving = ref(false)
const deleting = ref(false)
const search = ref('')
const dialog = ref(false)
const confirmOpen = ref(false)
const aprobarOpen = ref(false)
const aprobando = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<CotizacionVenta | null>(null)
const aprobarTarget = ref<CotizacionVenta | null>(null)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const headers = [
  { title: 'Código', key: 'codigo' }, { title: 'Cliente', key: 'cliente_id' },
  { title: 'Total', key: 'total' }, { title: 'Estado', key: 'estado' }, { title: 'Fecha', key: 'fecha' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 120 },
]

const ESTADOS_COTIZACION = ['BORRADOR', 'PENDIENTE', 'CONFIRMADA', 'CANCELADA']

function defaultDetalle(): DetalleVenta {
  return { producto_id: null, cantidad: 1, precio_unitario: 0 }
}

const form = reactive({
  cliente_id: null as number | null,
  estado: 'BORRADOR',
  observaciones: '',
  detalles: [defaultDetalle()] as DetalleVenta[],
})

const clienteMap = computed(() => Object.fromEntries(clientes.value.map((c) => [c.id, c.nombre])))

const totalCotizacion = computed(() =>
  form.detalles.reduce((acc, d) => acc + (Number(d.cantidad) || 0) * (Number(d.precio_unitario) || 0), 0),
)

async function loadData() {
  loading.value = true
  try {
    items.value = (await ventasService.getCotizaciones()).data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

async function loadCatalogos() {
  loadingCatalogos.value = true
  try {
    const [clientesRes, productosRes] = await Promise.all([
      ventasService.getClientes(),
      catalogosService.getProductos(),
    ])
    clientes.value = clientesRes.data
    productos.value = productosRes.data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loadingCatalogos.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    cliente_id: null,
    estado: 'BORRADOR',
    observaciones: '',
    detalles: [defaultDetalle()],
  })
  dialog.value = true
}

function openEdit(item: CotizacionVenta) {
  editingId.value = item.id
  Object.assign(form, {
    cliente_id: item.cliente_id,
    estado: item.estado,
    observaciones: item.observaciones ?? '',
    detalles: item.detalles.length
      ? item.detalles.map((d) => ({ producto_id: d.producto_id, cantidad: Number(d.cantidad), precio_unitario: Number(d.precio_unitario) }))
      : [defaultDetalle()],
  })
  dialog.value = true
}

function openDelete(item: CotizacionVenta) {
  deleteTarget.value = item
  confirmOpen.value = true
}

function openAprobar(item: CotizacionVenta) {
  aprobarTarget.value = item
  aprobarOpen.value = true
}

function agregarDetalle() {
  form.detalles.push(defaultDetalle())
}

function quitarDetalle(index: number) {
  if (form.detalles.length > 1) form.detalles.splice(index, 1)
}

function onProductoSelected(detalle: DetalleVenta) {
  const producto = productos.value.find((p) => p.id === detalle.producto_id)
  if (producto?.precio_actual != null) {
    detalle.precio_unitario = producto.precio_actual
  }
}

function bloquearDecimal(event: KeyboardEvent) {
  if (event.key === '.' || event.key === ',') {
    event.preventDefault()
  }
}

function onCantidadInput(detalle: DetalleVenta) {
  const n = Number(detalle.cantidad)
  if (Number.isFinite(n) && !Number.isInteger(n)) {
    detalle.cantidad = Math.trunc(n) || 1
  }
}

async function saveItem() {
  if (!(await formRef.value?.validate())?.valid) return
  if (!form.cliente_id) {
    appStore.showError('Seleccione un cliente')
    return
  }
  const detallesValidos = form.detalles.filter(
    (d): d is DetalleVenta & { producto_id: number } => !!d.producto_id && Number(d.cantidad) > 0,
  )
  if (!detallesValidos.length) {
    appStore.showError('Agregue al menos un producto con cantidad mayor a 0')
    return
  }

  saving.value = true
  try {
    const payload = {
      cliente_id: form.cliente_id,
      estado: form.estado,
      observaciones: form.observaciones || null,
      detalles: detallesValidos.map((d) => ({
        producto_id: d.producto_id,
        cantidad: Math.trunc(Number(d.cantidad)),
        precio_unitario: Number(d.precio_unitario),
      })),
    }
    if (editingId.value) {
      await ventasService.updateCotizacion(editingId.value, payload)
      appStore.showSuccess('Cotización actualizada')
    } else {
      await ventasService.createCotizacion(payload)
      appStore.showSuccess('Cotización creada')
    }
    dialog.value = false
    await loadData()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await ventasService.deleteCotizacion(deleteTarget.value.id)
    appStore.showSuccess('Cotización eliminada')
    confirmOpen.value = false
    await loadData()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    deleting.value = false
  }
}

async function confirmAprobar() {
  if (!aprobarTarget.value) return
  aprobando.value = true
  try {
    const { data: venta } = await ventasService.aprobarCotizacion(aprobarTarget.value.id)
    appStore.showSuccess(`Cotización aprobada. Venta generada: ${venta.codigo}`)
    aprobarOpen.value = false
    await loadData()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    aprobando.value = false
  }
}

onMounted(() => {
  loadData()
  loadCatalogos()
})
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Cotizaciones de venta" subtitle="Propuestas comerciales">
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nueva cotización</v-btn>
    </template>
    <template #item.cliente_id="{ value }">{{ clienteMap[value] ?? value }}</template>
    <template #item.estado="{ value }"><v-chip :color="ESTADO_VENTA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip></template>
    <template #item.actions="{ item }">
      <v-btn
        v-if="item.estado === 'PENDIENTE' || item.estado === 'BORRADOR'"
        icon="mdi-check-circle-outline"
        size="small"
        variant="text"
        color="success"
        @click="openAprobar(item)"
      />
      <v-btn icon="mdi-pencil-outline" size="small" variant="text" @click="openEdit(item)" />
      <v-btn icon="mdi-delete-outline" size="small" variant="text" color="error" @click="openDelete(item)" />
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="800" persistent scrollable>
    <v-card>
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-file-document-edit-outline" />
        {{ editingId ? 'Editar cotización' : 'Nueva cotización' }}
      </v-card-title>
      <v-divider />
      <v-card-text class="pa-5">
        <v-form ref="formRef">
          <v-row dense>
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.cliente_id"
                :items="clientes"
                item-title="nombre"
                item-value="id"
                label="Cliente"
                prepend-inner-icon="mdi-account-outline"
                :rules="[requiredRule]"
                :loading="loadingCatalogos"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-select
                v-model="form.estado"
                :items="ESTADOS_COTIZACION"
                label="Estado"
                prepend-inner-icon="mdi-flag-outline"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>

          <div class="d-flex align-center justify-space-between mb-2 mt-2">
            <div class="text-subtitle-2 font-weight-bold">Productos</div>
            <v-btn size="small" variant="tonal" prepend-icon="mdi-plus" @click="agregarDetalle">Agregar línea</v-btn>
          </div>

          <div v-for="(detalle, index) in form.detalles" :key="index" class="detalle-row">
            <v-select
              v-model="detalle.producto_id"
              :items="productos"
              item-title="nombre"
              item-value="id"
              label="Producto"
              :rules="[requiredRule]"
              :loading="loadingCatalogos"
              variant="outlined"
              density="compact"
              class="detalle-row__producto"
              @update:model-value="onProductoSelected(detalle)"
            />
            <v-text-field
              v-model.number="detalle.cantidad"
              label="Cantidad"
              type="number"
              min="1"
              step="1"
              :rules="[requiredRule, integerRule]"
              variant="outlined"
              density="compact"
              class="detalle-row__cantidad"
              @keydown="bloquearDecimal"
              @update:model-value="onCantidadInput(detalle)"
            />
            <v-text-field
              v-model.number="detalle.precio_unitario"
              label="Precio unitario"
              type="number"
              min="0"
              step="0.01"
              prefix="$"
              variant="outlined"
              density="compact"
              class="detalle-row__precio"
            />
            <v-btn
              icon="mdi-delete-outline"
              size="small"
              variant="text"
              color="error"
              :disabled="form.detalles.length === 1"
              @click="quitarDetalle(index)"
            />
          </div>

          <v-textarea
            v-model="form.observaciones"
            label="Observaciones"
            rows="2"
            variant="outlined"
            density="comfortable"
            class="mt-2"
          />

          <div class="text-right text-h6 font-weight-bold mt-2">
            Total: ${{ totalCotizacion.toFixed(2) }}
          </div>
        </v-form>
      </v-card-text>
      <v-divider />
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" :disabled="saving" @click="saveItem">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <ConfirmDialog
    v-model="confirmOpen"
    :loading="deleting"
    :message="`¿Eliminar la cotización «${deleteTarget?.codigo}»?`"
    @confirm="confirmDelete"
  />

  <ConfirmDialog
    v-model="aprobarOpen"
    title="Aprobar cotización"
    :message="`¿Aprobar la cotización «${aprobarTarget?.codigo}» y generar la venta correspondiente? Se descontará el stock y se generará la factura.`"
    confirm-text="Aprobar"
    confirm-color="success"
    icon="mdi-check-circle-outline"
    icon-color="success"
    :loading="aprobando"
    @confirm="confirmAprobar"
  />
</template>

<style scoped>
.detalle-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.detalle-row__producto {
  flex: 2;
}

.detalle-row__cantidad {
  flex: 1;
}

.detalle-row__precio {
  flex: 1;
}
</style>
