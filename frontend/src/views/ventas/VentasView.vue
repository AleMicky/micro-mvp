<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { ventasService } from '@/services/ventas.service'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import { useBarcodeScanner } from '@/composables/useBarcodeScanner'
import { ESTADO_VENTA_COLORS, type Cliente, type DetalleVenta, type Venta } from '@/types/ventas.types'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen } from '@/types/inventario.types'

const appStore = useAppStore()
const items = ref<Venta[]>([])
const clientes = ref<Cliente[]>([])
const productos = ref<Producto[]>([])
const almacenes = ref<Almacen[]>([])
const loading = ref(false)
const loadingCatalogos = ref(false)
const saving = ref(false)
const search = ref('')
const dialog = ref(false)
const ventaFormRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const headers = [
  { title: 'Código', key: 'codigo' }, { title: 'Cliente', key: 'cliente_id' },
  { title: 'Total', key: 'total' }, { title: 'Estado', key: 'estado' }, { title: 'Fecha', key: 'fecha' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const },
]

function defaultDetalle(): DetalleVenta {
  return { producto_id: 0, cantidad: 1, precio_unitario: 0 }
}

const form = reactive({
  cliente_id: null as number | null,
  almacen_id: null as number | null,
  observaciones: '',
  detalles: [defaultDetalle()] as DetalleVenta[],
})

const clienteMap = computed(() => Object.fromEntries(clientes.value.map((c) => [c.id, c.nombre])))

const totalVenta = computed(() =>
  form.detalles.reduce((acc, d) => acc + (Number(d.cantidad) || 0) * (Number(d.precio_unitario) || 0), 0),
)

async function loadData() {
  loading.value = true
  try {
    items.value = (await ventasService.getVentas()).data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

async function loadCatalogos() {
  loadingCatalogos.value = true
  try {
    const [clientesRes, productosRes, almacenesRes] = await Promise.all([
      ventasService.getClientes(),
      catalogosService.getProductos(),
      inventarioService.getAlmacenes(),
    ])
    clientes.value = clientesRes.data
    productos.value = productosRes.data
    almacenes.value = almacenesRes.data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loadingCatalogos.value = false
  }
}

function openCreate() {
  Object.assign(form, {
    cliente_id: null,
    almacen_id: almacenes.value[0]?.id ?? null,
    observaciones: '',
    detalles: [defaultDetalle()],
  })
  dialog.value = true
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

function agregarProductoPorCodigoBarras(codigo: string) {
  if (!dialog.value) return

  const producto = productos.value.find((p) => p.codigo_barras === codigo)
  if (!producto) {
    appStore.showError(`No se encontró ningún producto con el código de barras "${codigo}"`)
    return
  }

  const lineaExistente = form.detalles.find((d) => d.producto_id === producto.id)
  if (lineaExistente) {
    lineaExistente.cantidad = Number(lineaExistente.cantidad || 0) + 1
  } else {
    const lineaVacia = form.detalles.find((d) => !d.producto_id)
    const nuevaLinea: DetalleVenta = {
      producto_id: producto.id,
      cantidad: 1,
      precio_unitario: producto.precio_actual ?? 0,
    }
    if (lineaVacia) {
      Object.assign(lineaVacia, nuevaLinea)
    } else {
      form.detalles.push(nuevaLinea)
    }
  }

  appStore.showSuccess(`Producto agregado: ${producto.nombre}`)
}

useBarcodeScanner(agregarProductoPorCodigoBarras)

async function saveVenta() {
  if (!(await ventaFormRef.value?.validate())?.valid) return
  if (!form.cliente_id) {
    appStore.showError('Seleccione un cliente')
    return
  }
  const detallesValidos = form.detalles.filter((d) => d.producto_id && Number(d.cantidad) > 0)
  if (!detallesValidos.length) {
    appStore.showError('Agregue al menos un producto con cantidad mayor a 0')
    return
  }

  saving.value = true
  try {
    await ventasService.createVenta({
      cliente_id: form.cliente_id,
      almacen_id: form.almacen_id ?? undefined,
      observaciones: form.observaciones || null,
      detalles: detallesValidos.map((d) => ({
        producto_id: d.producto_id,
        cantidad: Number(d.cantidad),
        precio_unitario: Number(d.precio_unitario),
      })),
    })
    appStore.showSuccess('Venta creada')
    dialog.value = false
    await loadData()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    saving.value = false
  }
}

async function confirmar(item: Venta) {
  try { await ventasService.confirmarVenta(item.id); appStore.showSuccess('Venta confirmada'); await loadData() }
  catch (e) { appStore.showError(getErrorMessage(e)) }
}

onMounted(() => {
  loadData()
  loadCatalogos()
})
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Ventas" subtitle="Registro de ventas">
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nueva venta</v-btn>
    </template>
    <template #item.cliente_id="{ value }">{{ clienteMap[value] ?? value }}</template>
    <template #item.estado="{ value }"><v-chip :color="ESTADO_VENTA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip></template>
    <template #item.actions="{ item }">
      <v-btn v-if="['BORRADOR','PENDIENTE'].includes(item.estado)" size="small" color="primary" variant="tonal" @click="confirmar(item)">Confirmar</v-btn>
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="800" persistent scrollable>
    <v-card>
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-cart-arrow-up" />
        Nueva venta
        <v-chip size="small" color="success" variant="tonal" prepend-icon="mdi-barcode-scan" class="ml-2">
          Escáner activo
        </v-chip>
      </v-card-title>
      <v-divider />
      <v-card-text class="pa-5">
        <v-form ref="ventaFormRef">
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
                v-model="form.almacen_id"
                :items="almacenes"
                item-title="nombre"
                item-value="id"
                label="Almacén"
                prepend-inner-icon="mdi-warehouse"
                :loading="loadingCatalogos"
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
              variant="outlined"
              density="compact"
              class="detalle-row__producto"
              @update:model-value="onProductoSelected(detalle)"
            />
            <v-text-field
              v-model.number="detalle.cantidad"
              label="Cantidad"
              type="number"
              min="0.01"
              step="0.01"
              variant="outlined"
              density="compact"
              class="detalle-row__cantidad"
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
            Total: ${{ totalVenta.toFixed(2) }}
          </div>
        </v-form>
      </v-card-text>
      <v-divider />
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="saveVenta">Crear venta</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
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
