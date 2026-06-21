<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import MovimientosInventarioTable from '@/components/MovimientosInventarioTable.vue'
import PageHeader from '@/components/PageHeader.vue'
import { useMovimientosInventario } from '@/composables/useMovimientosInventario'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { formatInteger } from '@/utils/format'
import { positiveNumberRule, requiredRule } from '@/utils/validation'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen } from '@/types/inventario.types'

interface DetalleRow {
  key: number
  producto_id: number | null
  cantidad: number | null
}

const appStore = useAppStore()

const productos = ref<Producto[]>([])
const almacenes = ref<Almacen[]>([])
const existenciasOrigen = ref<Record<number, number>>({})
const catalogosReady = ref(false)
const loadingExistencias = ref(false)
const saving = ref(false)
const search = ref('')
const nextRowKey = ref(1)

const formRef = ref<{
  validate: () => Promise<{ valid: boolean }>
  resetValidation: () => void
} | null>(null)

const form = reactive({
  almacen_origen_id: null as number | null,
  almacen_destino_id: null as number | null,
  observaciones: '',
})

const { loading: loadingMovimientos, filteredRows, refresh: refreshMovimientos } =
  useMovimientosInventario()

const transferenciasBase = filteredRows({
  tipos: ['TRANSFERENCIA_SALIDA', 'TRANSFERENCIA_ENTRADA'],
})

const transferenciasVisibles = computed(() => {
  if (!form.almacen_origen_id && !form.almacen_destino_id) return transferenciasBase.value
  const ids = [form.almacen_origen_id, form.almacen_destino_id].filter(
    (id): id is number => id != null,
  )
  return transferenciasBase.value.filter((m) => ids.includes(m.almacen_id))
})

const detalles = ref<DetalleRow[]>([{ key: 0, producto_id: null, cantidad: null }])

const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))

const almacenesDestino = computed(() =>
  almacenes.value.filter((a) => a.id !== form.almacen_origen_id),
)

const almacenesOrigen = computed(() =>
  almacenes.value.filter((a) => a.id !== form.almacen_destino_id),
)

const validLineCount = computed(
  () => detalles.value.filter((d) => d.producto_id && d.cantidad && d.cantidad > 0).length,
)

const sameAlmacenRule = () =>
  form.almacen_origen_id !== form.almacen_destino_id || 'Origen y destino deben ser diferentes'

function stockOrigen(productoId: number | null): number | null {
  if (!productoId || !form.almacen_origen_id) return null
  const value = existenciasOrigen.value[productoId]
  return value !== undefined ? value : null
}

function cantidadExcedeStock(detalle: DetalleRow): boolean {
  const stock = stockOrigen(detalle.producto_id)
  if (stock === null || !detalle.cantidad) return false
  return detalle.cantidad > stock
}

function productosDisponibles(currentProductoId: number | null) {
  const usedIds = new Set(
    detalles.value.map((d) => d.producto_id).filter((id): id is number => id !== null && id !== currentProductoId),
  )
  return productos.value.filter((p) => !usedIds.has(p.id))
}

function productoFilter(_value: string, query: string, item?: { raw: Producto }) {
  const producto = item?.raw
  if (!producto) return false
  const term = query.trim().toLowerCase()
  if (!term) return true
  return (
    producto.nombre.toLowerCase().includes(term) ||
    producto.codigo.toLowerCase().includes(term) ||
    (producto.codigo_barras?.toLowerCase().includes(term) ?? false)
  )
}

function productoNombre(productoId: number | null): string {
  if (!productoId) return ''
  return productoMap.value[productoId] ?? ''
}

function swapAlmacenes() {
  const origen = form.almacen_origen_id
  form.almacen_origen_id = form.almacen_destino_id
  form.almacen_destino_id = origen
}

function addDetalle() {
  nextRowKey.value += 1
  detalles.value.push({ key: nextRowKey.value, producto_id: null, cantidad: null })
}

function removeDetalle(index: number) {
  if (detalles.value.length <= 1) return
  detalles.value.splice(index, 1)
}

function resetDetalles() {
  nextRowKey.value += 1
  detalles.value = [{ key: nextRowKey.value, producto_id: null, cantidad: null }]
}

async function loadCatalogos() {
  try {
    const [productosRes, almacenesRes] = await Promise.all([
      catalogosService.getProductos(),
      inventarioService.getAlmacenes(),
    ])
    productos.value = productosRes.data
    almacenes.value = almacenesRes.data
    catalogosReady.value = true
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  }
}

async function loadExistenciasOrigen(almacenId: number) {
  loadingExistencias.value = true
  try {
    const { data } = await inventarioService.getExistenciasByAlmacen(almacenId)
    existenciasOrigen.value = Object.fromEntries(data.map((e) => [e.producto_id, e.cantidad_actual]))
  } catch (error) {
    appStore.showError(getErrorMessage(error))
    existenciasOrigen.value = {}
  } finally {
    loadingExistencias.value = false
  }
}

async function submitForm() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid) return

  const validDetalles = detalles.value.filter((d) => d.producto_id && d.cantidad && d.cantidad > 0)
  if (!validDetalles.length) {
    appStore.showError('Agregue al menos un producto con cantidad')
    return
  }

  const excede = validDetalles.some((d) => cantidadExcedeStock(d))
  if (excede) {
    appStore.showError('Una o más cantidades superan el stock disponible en origen')
    return
  }

  saving.value = true
  try {
    await inventarioService.transferenciaStock({
      almacen_origen_id: form.almacen_origen_id!,
      almacen_destino_id: form.almacen_destino_id!,
      observaciones: form.observaciones.trim() || null,
      detalles: validDetalles.map((d) => ({
        producto_id: d.producto_id!,
        cantidad: d.cantidad!,
      })),
    })
    appStore.showSuccess('Transferencia registrada')
    form.observaciones = ''
    resetDetalles()
    formRef.value?.resetValidation()
    await Promise.all([
      refreshMovimientos(),
      form.almacen_origen_id ? loadExistenciasOrigen(form.almacen_origen_id) : Promise.resolve(),
    ])
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

watch(
  () => form.almacen_origen_id,
  async (almacenId) => {
    if (almacenId) {
      await loadExistenciasOrigen(almacenId)
    } else {
      existenciasOrigen.value = {}
    }
  },
)

onMounted(async () => {
  await Promise.all([loadCatalogos(), refreshMovimientos()])
})
</script>

<template>
  <div class="transfer-page">
    <PageHeader
      title="Transferencia de stock"
      subtitle="Mueve mercancía entre almacenes"
      icon="mdi-truck-delivery-outline"
    />

    <div class="transfer-page__grid">
      <v-card class="transfer-panel" border elevation="0">
        <div class="transfer-panel__header">
          <div class="transfer-panel__title">
            <v-icon icon="mdi-swap-horizontal" size="16" color="primary" />
            <span>Nueva transferencia</span>
          </div>
          <v-chip v-if="validLineCount" size="x-small" variant="tonal" color="primary" label>
            {{ validLineCount }} producto(s)
          </v-chip>
        </div>

        <v-form ref="formRef" class="transfer-form" @submit.prevent="submitForm">
          <div class="almacenes-row">
            <v-autocomplete
              v-model="form.almacen_origen_id"
              :items="almacenesOrigen"
              item-title="nombre"
              item-value="id"
              label="Origen"
              density="compact"
              hide-details="auto"
              :rules="[requiredRule, sameAlmacenRule]"
              prepend-inner-icon="mdi-warehouse"
              clearable
              class="almacenes-row__field"
            />
            <v-btn
              icon="mdi-swap-horizontal"
              variant="text"
              size="x-small"
              color="primary"
              class="almacenes-row__swap"
              :disabled="!form.almacen_origen_id && !form.almacen_destino_id"
              aria-label="Intercambiar almacenes"
              @click="swapAlmacenes"
            />
            <v-autocomplete
              v-model="form.almacen_destino_id"
              :items="almacenesDestino"
              item-title="nombre"
              item-value="id"
              label="Destino"
              density="compact"
              hide-details="auto"
              :rules="[requiredRule, sameAlmacenRule]"
              prepend-inner-icon="mdi-warehouse"
              clearable
              class="almacenes-row__field"
            />
          </div>

          <v-text-field
            v-model="form.observaciones"
            label="Observaciones"
            density="compact"
            hide-details
            placeholder="Opcional"
            prepend-inner-icon="mdi-note-text-outline"
          />

          <div class="detalle-block">
            <div class="detalle-block__head">
              <span class="detalle-block__label">Productos</span>
              <v-btn
                size="x-small"
                variant="tonal"
                color="primary"
                prepend-icon="mdi-plus"
                :disabled="!form.almacen_origen_id || !form.almacen_destino_id"
                @click="addDetalle"
              >
                Agregar
              </v-btn>
            </div>

            <v-alert
              v-if="!form.almacen_origen_id || !form.almacen_destino_id"
              type="info"
              variant="tonal"
              density="compact"
              class="detalle-block__alert"
            >
              Selecciona almacén origen y destino para agregar productos.
            </v-alert>

            <div v-else class="detalle-list">
              <div
                v-for="(detalle, index) in detalles"
                :key="detalle.key"
                class="detalle-row"
              >
                <div
                  class="detalle-row__producto"
                  :title="productoNombre(detalle.producto_id) || undefined"
                >
                  <v-autocomplete
                    v-model="detalle.producto_id"
                    :items="productosDisponibles(detalle.producto_id)"
                    item-title="nombre"
                    item-value="id"
                    label="Producto"
                    placeholder="Buscar por nombre o código"
                    density="compact"
                    hide-details
                    clearable
                    :custom-filter="productoFilter"
                    :menu-props="{ maxWidth: 520, contentClass: 'detalle-producto-menu' }"
                  >
                    <template #item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="item.raw.nombre"
                        :subtitle="item.raw.codigo"
                        prepend-icon="mdi-package-variant"
                      />
                    </template>
                  </v-autocomplete>
                </div>

                <div class="detalle-row__meta">
                  <div class="detalle-row__stock">
                    <span class="detalle-row__field-label">Disp.</span>
                    <v-skeleton-loader v-if="loadingExistencias" type="text" width="32" />
                    <span
                      v-else
                      class="stock-badge"
                      :class="{ 'stock-badge--empty': stockOrigen(detalle.producto_id) === null }"
                    >
                      {{
                        detalle.producto_id
                          ? formatInteger(stockOrigen(detalle.producto_id) ?? 0)
                          : '—'
                      }}
                    </span>
                  </div>

                  <v-text-field
                    v-model.number="detalle.cantidad"
                    label="Cantidad"
                    type="number"
                    min="1"
                    step="1"
                    density="compact"
                    hide-details="auto"
                    :rules="detalle.producto_id ? [requiredRule, positiveNumberRule] : []"
                    :disabled="!detalle.producto_id"
                    :class="['detalle-row__cantidad', { 'text-error': cantidadExcedeStock(detalle) }]"
                  />

                  <v-btn
                    icon="mdi-close"
                    variant="text"
                    size="x-small"
                    color="error"
                    class="detalle-row__remove"
                    :disabled="detalles.length === 1"
                    aria-label="Quitar línea"
                    @click="removeDetalle(index)"
                  />
                </div>
              </div>
            </div>
          </div>

          <div class="transfer-form__footer">
            <v-btn
              color="primary"
              variant="flat"
              size="small"
              block
              prepend-icon="mdi-truck-delivery-outline"
              :loading="saving"
              :disabled="!catalogosReady || !form.almacen_origen_id || !form.almacen_destino_id"
              type="submit"
            >
              Registrar transferencia
            </v-btn>
          </div>
        </v-form>
      </v-card>

      <div class="historial-section">
        <MovimientosInventarioTable
          v-model:search="search"
          :items="transferenciasVisibles"
          :loading="loadingMovimientos"
          title="Transferencias recientes"
          subtitle="Historial de movimientos entre almacenes"
          @refresh="refreshMovimientos"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.transfer-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.transfer-page__grid {
  display: grid;
  grid-template-columns: minmax(360px, 500px) minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.transfer-panel {
  position: sticky;
  top: calc(var(--mac-topbar-h) + 12px);
  overflow: hidden;
  background: #fff;
}

.transfer-panel::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: rgb(var(--v-theme-primary));
  border-radius: 3px 0 0 3px;
}

.transfer-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 14px 10px 16px;
  border-bottom: 1px solid var(--mac-border);
}

.transfer-panel__title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--mac-text-sm);
  font-weight: 600;
}

.transfer-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 14px 14px 16px;
}

.almacenes-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 4px;
  align-items: flex-start;
}

.almacenes-row__swap {
  margin-top: 6px;
}

.detalle-block {
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  overflow: hidden;
  background: rgba(var(--v-theme-primary), 0.02);
}

.detalle-block__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(var(--v-theme-on-surface), 0.03);
  border-bottom: 1px solid var(--mac-border);
}

.detalle-block__label {
  font-size: var(--mac-text-xs);
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.7);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detalle-block__alert {
  margin: 10px;
}

.detalle-list {
  display: flex;
  flex-direction: column;
}

.detalle-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
}

.detalle-row + .detalle-row {
  border-top: 1px solid var(--mac-border);
}

.detalle-row__producto {
  min-width: 0;
}

.detalle-row__producto :deep(.v-field__input) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detalle-row__meta {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) 28px;
  gap: 8px;
  align-items: start;
}

.detalle-row__stock {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 56px;
  padding-top: 2px;
}

.detalle-row__field-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.5);
  line-height: 1;
}

.detalle-row__remove {
  margin-top: 6px;
}

.detalle-row__cantidad :deep(input) {
  font-weight: 600;
  text-align: right;
}

.stock-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 24px;
  padding: 0 6px;
  border-radius: 5px;
  background: rgba(var(--v-theme-on-surface), 0.06);
  font-size: var(--mac-text-xs);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.stock-badge--empty {
  color: rgba(var(--v-theme-on-surface), 0.4);
}

.transfer-form__footer {
  margin-top: 2px;
  padding-top: 10px;
  border-top: 1px solid var(--mac-border);
}

.historial-section {
  min-width: 0;
}

.cell-ellipsis {
  display: block;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 960px) {
  .transfer-page__grid {
    grid-template-columns: 1fr;
  }

  .transfer-panel {
    position: static;
  }
}

@media (max-width: 600px) {
  .almacenes-row {
    grid-template-columns: 1fr;
  }

  .almacenes-row__swap {
    justify-self: center;
    margin: 0;
    transform: rotate(90deg);
  }

  .detalle-row__meta {
    grid-template-columns: minmax(0, 1fr) 28px;
  }

  .detalle-row__stock {
    display: none;
  }

  .cell-ellipsis {
    max-width: 100px;
  }
}
</style>

<style>
.detalle-producto-menu .v-list-item-title {
  white-space: normal;
  line-height: 1.35;
}

.detalle-producto-menu .v-list-item-subtitle {
  opacity: 0.72;
}
</style>
