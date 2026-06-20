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
import { nonNegativeRule, requiredRule } from '@/utils/validation'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen } from '@/types/inventario.types'

interface DetalleRow {
  key: number
  producto_id: number | null
  cantidad_nueva: number | null
}

const appStore = useAppStore()

const productos = ref<Producto[]>([])
const almacenes = ref<Almacen[]>([])
const existenciasMap = ref<Record<number, number>>({})
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
  almacen_id: null as number | null,
  motivo: '',
  observaciones: '',
})

const { loading: loadingMovimientos, filteredRows, refresh: refreshMovimientos } =
  useMovimientosInventario()

const almacenFilter = computed(() => form.almacen_id)
const ajustesVisibles = filteredRows({
  almacenId: almacenFilter,
  tipos: ['AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO'],
})

const detalles = ref<DetalleRow[]>([{ key: 0, producto_id: null, cantidad_nueva: null }])

const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))

const almacenNombre = computed(
  () => almacenes.value.find((a) => a.id === form.almacen_id)?.nombre ?? '',
)

const validLineCount = computed(
  () => detalles.value.filter((d) => hasCambio(d)).length,
)

function stockActualOrZero(productoId: number | null): number {
  if (!productoId || !form.almacen_id) return 0
  return Number(existenciasMap.value[productoId] ?? 0)
}

function stockActual(productoId: number | null): number | null {
  if (!productoId || !form.almacen_id) return null
  const value = existenciasMap.value[productoId]
  return value !== undefined ? value : null
}

function hasCambio(detalle: DetalleRow): boolean {
  if (!detalle.producto_id || detalle.cantidad_nueva === null) return false
  return Number(detalle.cantidad_nueva) !== stockActualOrZero(detalle.producto_id)
}

function cantidadNuevaRules(detalle: DetalleRow) {
  return [
    requiredRule,
    nonNegativeRule,
    (value: unknown) => {
      if (!detalle.producto_id || value === null || value === '') return true
      const nueva = Number(value)
      if (Number.isNaN(nueva)) return 'Valor inválido'
      if (nueva === stockActualOrZero(detalle.producto_id)) {
        return 'Debe ser distinta al stock actual'
      }
      return true
    },
  ]
}

function deltaClass(detalle: DetalleRow): string {
  const actual = stockActualOrZero(detalle.producto_id)
  if (!detalle.producto_id || detalle.cantidad_nueva === null) return ''
  if (detalle.cantidad_nueva === actual) return 'text-warning'
  if (detalle.cantidad_nueva > actual) return 'text-success'
  if (detalle.cantidad_nueva < actual) return 'text-error'
  return 'text-medium-emphasis'
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

function addDetalle() {
  nextRowKey.value += 1
  detalles.value.push({ key: nextRowKey.value, producto_id: null, cantidad_nueva: null })
}

function removeDetalle(index: number) {
  if (detalles.value.length <= 1) return
  detalles.value.splice(index, 1)
}

function resetDetalles() {
  nextRowKey.value += 1
  detalles.value = [{ key: nextRowKey.value, producto_id: null, cantidad_nueva: null }]
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

async function loadExistencias(almacenId: number) {
  loadingExistencias.value = true
  try {
    const { data } = await inventarioService.getExistenciasByAlmacen(almacenId)
    existenciasMap.value = Object.fromEntries(data.map((e) => [e.producto_id, e.cantidad_actual]))
  } catch (error) {
    appStore.showError(getErrorMessage(error))
    existenciasMap.value = {}
  } finally {
    loadingExistencias.value = false
  }
}

async function submitForm() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid) return

  const validDetalles = detalles.value.filter(
    (d) => d.producto_id && d.cantidad_nueva !== null && d.cantidad_nueva >= 0,
  )
  if (!validDetalles.length) {
    appStore.showError('Agregue al menos un producto con cantidad nueva')
    return
  }

  const detallesConCambio = validDetalles.filter(hasCambio)
  if (!detallesConCambio.length) {
    appStore.showError('La cantidad nueva debe ser distinta al stock actual en al menos un producto')
    return
  }

  saving.value = true
  try {
    await inventarioService.ajusteStock({
      almacen_id: form.almacen_id!,
      motivo: form.motivo.trim() || null,
      observaciones: form.observaciones.trim() || null,
      detalles: detallesConCambio.map((d) => ({
        producto_id: d.producto_id!,
        cantidad_nueva: d.cantidad_nueva!,
      })),
    })
    appStore.showSuccess('Ajuste de stock registrado')
    form.motivo = ''
    form.observaciones = ''
    resetDetalles()
    formRef.value?.resetValidation()
    await Promise.all([
      refreshMovimientos(),
      form.almacen_id ? loadExistencias(form.almacen_id) : Promise.resolve(),
    ])
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

watch(
  () => form.almacen_id,
  async (almacenId) => {
    if (almacenId) {
      await loadExistencias(almacenId)
    } else {
      existenciasMap.value = {}
    }
  },
)

onMounted(async () => {
  await Promise.all([loadCatalogos(), refreshMovimientos()])
})
</script>

<template>
  <div class="ajuste-page">
    <PageHeader
      title="Ajuste de stock"
      subtitle="Corrige cantidades reales en un almacén"
      icon="mdi-tune-vertical"
    />

    <div class="ajuste-page__grid">
      <v-card class="ajuste-panel" border elevation="0">
        <div class="ajuste-panel__header">
          <div class="ajuste-panel__title">
            <v-icon icon="mdi-warehouse" size="16" color="warning" />
            <span>Datos del ajuste</span>
          </div>
          <v-chip v-if="validLineCount" size="x-small" variant="tonal" color="warning" label>
            {{ validLineCount }} cambio(s)
          </v-chip>
        </div>

        <v-form ref="formRef" class="ajuste-form" @submit.prevent="submitForm">
          <v-autocomplete
            v-model="form.almacen_id"
            :items="almacenes"
            item-title="nombre"
            item-value="id"
            label="Almacén"
            density="compact"
            hide-details="auto"
            :rules="[requiredRule]"
            prepend-inner-icon="mdi-warehouse"
            clearable
          />

          <div class="ajuste-form__meta">
            <v-text-field
              v-model="form.motivo"
              label="Motivo"
              density="compact"
              hide-details
              placeholder="Ej. conteo físico"
              prepend-inner-icon="mdi-tag-outline"
            />
            <v-text-field
              v-model="form.observaciones"
              label="Observaciones"
              density="compact"
              hide-details
              placeholder="Opcional"
              prepend-inner-icon="mdi-note-text-outline"
            />
          </div>

          <div class="detalle-block">
            <div class="detalle-block__head">
              <span class="detalle-block__label">Productos a ajustar</span>
              <v-btn
                size="x-small"
                variant="tonal"
                color="warning"
                prepend-icon="mdi-plus"
                :disabled="!form.almacen_id"
                @click="addDetalle"
              >
                Agregar
              </v-btn>
            </div>

            <v-alert
              v-if="!form.almacen_id"
              type="info"
              variant="tonal"
              density="compact"
              class="detalle-block__alert"
            >
              Selecciona un almacén para ver el stock actual y agregar productos.
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
                  <div class="detalle-row__actual">
                    <span class="detalle-row__field-label">Actual</span>
                    <v-skeleton-loader v-if="loadingExistencias" type="text" width="32" />
                    <span
                      v-else
                      class="stock-badge"
                      :class="{ 'stock-badge--empty': stockActual(detalle.producto_id) === null }"
                    >
                      {{
                        detalle.producto_id
                          ? formatInteger(stockActual(detalle.producto_id) ?? 0)
                          : '—'
                      }}
                    </span>
                  </div>

                  <v-text-field
                    v-model.number="detalle.cantidad_nueva"
                    label="Nueva cantidad"
                    type="number"
                    min="0"
                    step="1"
                    density="compact"
                    hide-details="auto"
                    :rules="detalle.producto_id ? cantidadNuevaRules(detalle) : []"
                    :disabled="!detalle.producto_id"
                    :class="['detalle-row__nueva', deltaClass(detalle)]"
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

          <div class="ajuste-form__footer">
            <v-btn
              color="warning"
              variant="flat"
              size="small"
              block
              prepend-icon="mdi-tune-vertical"
              :loading="saving"
              :disabled="!catalogosReady || !form.almacen_id"
              type="submit"
            >
              Registrar ajuste
            </v-btn>
          </div>
        </v-form>
      </v-card>

      <div class="historial-section">
        <MovimientosInventarioTable
          v-model:search="search"
          :items="ajustesVisibles"
          :loading="loadingMovimientos"
          :title="form.almacen_id ? `Ajustes — ${almacenNombre}` : 'Ajustes recientes'"
          subtitle="Historial de correcciones de inventario"
          :show-almacen="!form.almacen_id"
          @refresh="refreshMovimientos"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.ajuste-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ajuste-page__grid {
  display: grid;
  grid-template-columns: minmax(360px, 500px) minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.ajuste-panel {
  position: sticky;
  top: calc(var(--mac-topbar-h) + 12px);
  overflow: hidden;
  background: #fff;
}

.ajuste-panel::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: rgb(var(--v-theme-warning));
  border-radius: 3px 0 0 3px;
}

.ajuste-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 14px 10px 16px;
  border-bottom: 1px solid var(--mac-border);
}

.ajuste-panel__title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--mac-text-sm);
  font-weight: 600;
  color: rgb(var(--v-theme-on-surface));
}

.ajuste-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 14px 14px 16px;
}

.ajuste-form__meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.detalle-block {
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  overflow: hidden;
  background: rgba(var(--v-theme-warning), 0.03);
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

.detalle-row__actual {
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

.stock-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 24px;
  padding: 0 6px;
  border-radius: 5px;
  background: rgba(var(--v-theme-on-surface), 0.06);
  font-size: var(--mac-text-xs);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: rgb(var(--v-theme-on-surface));
}

.stock-badge--empty {
  color: rgba(var(--v-theme-on-surface), 0.4);
}

.detalle-row__nueva :deep(input) {
  font-weight: 600;
  text-align: right;
}

.ajuste-form__footer {
  margin-top: 2px;
  padding-top: 10px;
  border-top: 1px solid var(--mac-border);
}

.historial-section {
  min-width: 0;
}

.cell-ellipsis {
  display: block;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-delta {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: rgba(var(--v-theme-on-surface), 0.6);
  white-space: nowrap;
}

@media (max-width: 960px) {
  .ajuste-page__grid {
    grid-template-columns: 1fr;
  }

  .ajuste-panel {
    position: static;
  }
}

@media (max-width: 600px) {
  .ajuste-form__meta {
    grid-template-columns: 1fr;
  }

  .detalle-row__meta {
    grid-template-columns: minmax(0, 1fr) 28px;
  }

  .detalle-row__actual {
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
