<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDataTable from '@/components/BaseDataTable.vue'
import PageHeader from '@/components/PageHeader.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { positiveNumberRule, requiredRule } from '@/utils/validation'
import { formatInteger } from '@/utils/format'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen, MovimientoInventario, TipoMovimiento } from '@/types/inventario.types'

type OperacionTab = 'ingreso' | 'salida'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const activeTab = ref<OperacionTab>('ingreso')
const productos = ref<Producto[]>([])
const almacenes = ref<Almacen[]>([])
const movimientos = ref<MovimientoInventario[]>([])
const catalogosReady = ref(false)
const loadingMovimientos = ref(false)
const saving = ref(false)
const search = ref('')
const formRef = ref<{
  validate: () => Promise<{ valid: boolean }>
  resetValidation: () => void
} | null>(null)
const historialRef = ref<HTMLElement | null>(null)

const form = reactive({
  producto_id: null as number | null,
  almacen_id: null as number | null,
  cantidad: null as number | null,
  stock_minimo: null as number | null,
  stock_maximo: null as number | null,
  observaciones: '',
})

const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))
const almacenMap = computed(() => Object.fromEntries(almacenes.value.map((a) => [a.id, a.nombre])))

const tabMeta: Record<
  OperacionTab,
  { label: string; icon: string; color: string; submitLabel: string; successMsg: string; hint: string }
> = {
  ingreso: {
    label: 'Ingreso',
    icon: 'mdi-arrow-down-bold',
    color: 'success',
    submitLabel: 'Registrar ingreso',
    successMsg: 'Ingreso de stock registrado',
    hint: 'Entrada de mercancía al almacén',
  },
  salida: {
    label: 'Salida',
    icon: 'mdi-arrow-up-bold',
    color: 'error',
    submitLabel: 'Registrar salida',
    successMsg: 'Salida de stock registrada',
    hint: 'Salida de mercancía del almacén',
  },
}

const headers = [
  { title: 'Tipo', key: 'tipo', width: 108 },
  { title: 'Producto', key: 'producto_id' },
  { title: 'Almacén', key: 'almacen_id' },
  { title: 'Cant.', key: 'cantidad', align: 'end' as const, width: 72 },
  { title: 'Stock', key: 'stock', align: 'center' as const, width: 100, sortable: false },
  { title: 'Obs.', key: 'observaciones', width: 120 },
  { title: 'Fecha', key: 'creado_en', width: 130 },
]

const tipoConfig: Record<TipoMovimiento, { color: string; label: string }> = {
  INGRESO: { color: 'success', label: 'Ingreso' },
  SALIDA: { color: 'error', label: 'Salida' },
  AJUSTE_POSITIVO: { color: 'info', label: 'Ajuste +' },
  AJUSTE_NEGATIVO: { color: 'warning', label: 'Ajuste −' },
  TRANSFERENCIA_SALIDA: { color: 'secondary', label: 'Trans. salida' },
  TRANSFERENCIA_ENTRADA: { color: 'primary', label: 'Trans. entrada' },
}

function resolveTabFromQuery(): OperacionTab {
  return route.query.tab === 'salida' ? 'salida' : 'ingreso'
}

function setTab(tab: OperacionTab) {
  if (activeTab.value === tab) return
  activeTab.value = tab
  router.replace({ query: { ...route.query, tab } })
}

function resetFormFields() {
  form.cantidad = null
  form.stock_minimo = null
  form.stock_maximo = null
  form.observaciones = ''
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

async function loadMovimientos() {
  loadingMovimientos.value = true
  try {
    const { data } = await inventarioService.getMovimientos()
    movimientos.value = data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loadingMovimientos.value = false
  }
}

async function submitForm() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid) return

  saving.value = true
  try {
    if (activeTab.value === 'ingreso') {
      await inventarioService.ingresoStock({
        producto_id: form.producto_id!,
        almacen_id: form.almacen_id!,
        cantidad: form.cantidad!,
        stock_minimo: form.stock_minimo,
        stock_maximo: form.stock_maximo,
        observaciones: form.observaciones.trim() || null,
      })
    } else {
      await inventarioService.salidaStock({
        producto_id: form.producto_id!,
        almacen_id: form.almacen_id!,
        cantidad: form.cantidad!,
        observaciones: form.observaciones.trim() || null,
      })
    }

    appStore.showSuccess(tabMeta[activeTab.value].successMsg)
    resetFormFields()
    formRef.value?.resetValidation()
    await loadMovimientos()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleString('es-MX', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

watch(
  () => route.query.tab,
  () => {
    activeTab.value = resolveTabFromQuery()
  },
)

onMounted(async () => {
  activeTab.value = resolveTabFromQuery()
  await Promise.all([loadCatalogos(), loadMovimientos()])

  if (route.query.view === 'historial') {
    requestAnimationFrame(() => {
      historialRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }
})
</script>

<template>
  <div class="stock-ops">
    <PageHeader
      title="Operaciones de stock"
      subtitle="Registra entradas y salidas, y consulta el historial reciente"
      icon="mdi-swap-vertical"
    />

    <div class="stock-ops__grid">
      <v-card
        class="ops-panel"
        :class="`ops-panel--${activeTab}`"
        border
        elevation="0"
      >
        <div class="ops-panel__header">
          <div class="segmented" role="tablist">
            <button
              v-for="tab in (['ingreso', 'salida'] as OperacionTab[])"
              :key="tab"
              type="button"
              role="tab"
              class="segmented__btn"
              :class="{ 'segmented__btn--active': activeTab === tab }"
              :aria-selected="activeTab === tab"
              @click="setTab(tab)"
            >
              <v-icon :icon="tabMeta[tab].icon" size="14" />
              {{ tabMeta[tab].label }}
            </button>
          </div>
          <p class="ops-panel__hint">{{ tabMeta[activeTab].hint }}</p>
        </div>

        <v-form ref="formRef" class="ops-form" @submit.prevent="submitForm">
          <div class="ops-form__fields">
            <v-autocomplete
              v-model="form.producto_id"
              :items="productos"
              item-title="nombre"
              item-value="id"
              label="Producto"
              density="compact"
              hide-details="auto"
              :rules="[requiredRule]"
              prepend-inner-icon="mdi-package-variant"
              clearable
            />
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
            <v-text-field
              v-model.number="form.cantidad"
              label="Cantidad"
              type="number"
              min="0"
              step="0.01"
              density="compact"
              hide-details="auto"
              :rules="[requiredRule, positiveNumberRule]"
              prepend-inner-icon="mdi-counter"
            />

            <div class="ops-form__extras" :class="{ 'ops-form__extras--open': activeTab === 'ingreso' }">
              <v-text-field
                v-model.number="form.stock_minimo"
                label="Stock mínimo"
                type="number"
                min="0"
                density="compact"
                hide-details
                placeholder="Opcional"
                tabindex="-1"
              />
              <v-text-field
                v-model.number="form.stock_maximo"
                label="Stock máximo"
                type="number"
                min="0"
                density="compact"
                hide-details
                placeholder="Opcional"
                tabindex="-1"
              />
            </div>

            <v-text-field
              v-model="form.observaciones"
              label="Observaciones"
              density="compact"
              hide-details
              placeholder="Opcional"
              prepend-inner-icon="mdi-note-text-outline"
              class="ops-form__notes"
            />
          </div>

          <div class="ops-form__footer">
            <v-btn
              :color="tabMeta[activeTab].color"
              variant="flat"
              size="small"
              block
              :prepend-icon="tabMeta[activeTab].icon"
              :loading="saving"
              :disabled="!catalogosReady"
              type="submit"
            >
              {{ tabMeta[activeTab].submitLabel }}
            </v-btn>
          </div>
        </v-form>
      </v-card>

      <div ref="historialRef" class="historial-section">
        <BaseDataTable
          v-model:search="search"
          :items="movimientos as Record<string, unknown>[]"
          :headers="headers"
          :loading="loadingMovimientos"
          title="Historial"
          subtitle="Movimientos recientes"
          search-label="Buscar..."
          empty-subtitle="Los movimientos aparecerán aquí después de registrar operaciones."
        >
          <template #actions>
            <v-btn
              icon="mdi-refresh"
              variant="text"
              size="small"
              :loading="loadingMovimientos"
              aria-label="Actualizar historial"
              @click="loadMovimientos"
            />
          </template>

          <template #item.tipo="{ value }">
            <v-chip
              :color="tipoConfig[value as TipoMovimiento]?.color ?? 'default'"
              size="x-small"
              variant="tonal"
              label
            >
              {{ tipoConfig[value as TipoMovimiento]?.label ?? value }}
            </v-chip>
          </template>

          <template #item.producto_id="{ value }">
            <span class="cell-ellipsis" :title="productoMap[value] ?? String(value)">
              {{ productoMap[value] ?? value }}
            </span>
          </template>

          <template #item.almacen_id="{ value }">
            <span class="cell-ellipsis" :title="almacenMap[value] ?? String(value)">
              {{ almacenMap[value] ?? value }}
            </span>
          </template>

          <template #item.cantidad="{ value, item }">
            <span
              class="cantidad-cell font-weight-medium"
              :class="{
                'text-success': item.tipo === 'INGRESO' || item.tipo === 'AJUSTE_POSITIVO' || item.tipo === 'TRANSFERENCIA_ENTRADA',
                'text-error': item.tipo === 'SALIDA' || item.tipo === 'AJUSTE_NEGATIVO' || item.tipo === 'TRANSFERENCIA_SALIDA',
              }"
            >
              {{ formatInteger(value) }}
            </span>
          </template>

          <template #item.stock="{ item }">
            <span class="stock-delta text-caption">
              {{ formatInteger(item.cantidad_anterior) }}
              <v-icon icon="mdi-arrow-right-thin" size="12" />
              <strong>{{ formatInteger(item.cantidad_nueva) }}</strong>
            </span>
          </template>

          <template #item.observaciones="{ value }">
            <span class="cell-ellipsis text-medium-emphasis" :title="value ?? ''">
              {{ value || '—' }}
            </span>
          </template>

          <template #item.creado_en="{ value }">
            <span class="text-caption text-medium-emphasis">{{ formatDate(value) }}</span>
          </template>
        </BaseDataTable>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stock-ops {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.stock-ops__grid {
  display: grid;
  grid-template-columns: minmax(300px, 360px) minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

/* Panel de operación */
.ops-panel {
  --ops-accent: rgb(var(--v-theme-primary));
  position: sticky;
  top: calc(var(--mac-topbar-h) + 12px);
  overflow: hidden;
  background: #fff;
}

.ops-panel--ingreso {
  --ops-accent: rgb(var(--v-theme-success));
}

.ops-panel--salida {
  --ops-accent: rgb(var(--v-theme-error));
}

.ops-panel::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--ops-accent);
  border-radius: 3px 0 0 3px;
}

.ops-panel__header {
  padding: 12px 14px 10px 16px;
  border-bottom: 1px solid var(--mac-border);
}

.ops-panel__hint {
  margin: 8px 0 0;
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.55);
  line-height: 1.35;
}

/* Segmented control */
.segmented {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  padding: 3px;
  background: rgba(var(--v-theme-on-surface), 0.05);
  border-radius: var(--mac-radius-sm);
}

.segmented__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 30px;
  border: none;
  border-radius: 5px;
  background: transparent;
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-family: inherit;
  font-size: var(--mac-text-xs);
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, box-shadow 0.15s ease;
}

.segmented__btn:hover:not(.segmented__btn--active) {
  color: rgba(var(--v-theme-on-surface), 0.85);
  background: rgba(255, 255, 255, 0.5);
}

.segmented__btn--active {
  background: #fff;
  color: rgb(var(--v-theme-on-surface));
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.ops-panel--ingreso .segmented__btn--active {
  color: rgb(var(--v-theme-success));
}

.ops-panel--salida .segmented__btn--active {
  color: rgb(var(--v-theme-error));
}

/* Formulario */
.ops-form {
  padding: 12px 14px 14px 16px;
}

.ops-form__fields {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ops-form__extras {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  pointer-events: none;
  transition: max-height 0.22s ease, opacity 0.18s ease, margin 0.22s ease;
  margin-top: 0;
}

.ops-form__extras--open {
  max-height: 56px;
  opacity: 1;
  pointer-events: auto;
  margin-top: 0;
}

.ops-form__notes {
  margin-top: 0;
}

.ops-form__footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--mac-border);
}

.historial-section {
  min-width: 0;
  scroll-margin-top: 72px;
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

.cantidad-cell {
  font-variant-numeric: tabular-nums;
}

@media (max-width: 960px) {
  .stock-ops__grid {
    grid-template-columns: 1fr;
  }

  .ops-panel {
    position: static;
  }
}

@media (max-width: 600px) {
  .cell-ellipsis {
    max-width: 100px;
  }
}
</style>
