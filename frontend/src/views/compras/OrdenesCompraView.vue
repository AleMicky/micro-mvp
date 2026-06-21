<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
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
const filterEstado = ref<'all' | 'BORRADOR' | 'APROBADA' | 'CANCELADA'>('all')
const filterProveedor = ref<number | null>(null)
const dialog = ref(false)
const detailDialog = ref(false)
const confirmOpen = ref(false)
const confirmAction = ref<'delete' | 'cancel' | null>(null)
const saving = ref(false)
const acting = ref(false)
const actingId = ref<number | null>(null)
const editingId = ref<number | null>(null)
const editingProveedorId = ref<number | null>(null)
const actionTarget = ref<OrdenCompra | null>(null)
const detailItem = ref<OrdenCompra | null>(null)
const nextRowKey = ref(1)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = reactive({
  fecha: new Date().toISOString().slice(0, 10),
  observacion: '',
})
const detalles = ref<DetalleRow[]>([{ key: 0, producto_id: null, cantidad: null, precio_unitario: null }])

const proveedorMap = computed(() => Object.fromEntries(proveedores.value.map((p) => [p.id, p.nombre])))
const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))

const dialogProveedorId = computed(() =>
  editingId.value ? editingProveedorId.value : filterProveedor.value,
)
const dialogProveedorNombre = computed(() =>
  dialogProveedorId.value ? proveedorMap.value[dialogProveedorId.value] : null,
)

const proveedorItems = computed(() => {
  if (!filterProveedor.value) return []
  return items.value.filter((i) => i.proveedor_id === filterProveedor.value)
})

const proveedorSeleccionado = computed(() =>
  proveedores.value.find((p) => p.id === filterProveedor.value) ?? null,
)

const stats = computed(() => {
  const base = proveedorItems.value
  const borradores = base.filter((i) => i.estado === 'BORRADOR').length
  const aprobadas = base.filter((i) => i.estado === 'APROBADA').length
  const montoAprobado = base
    .filter((i) => i.estado === 'APROBADA')
    .reduce((acc, i) => acc + Number(i.total), 0)
  return { total: base.length, borradores, aprobadas, montoAprobado }
})

const hasFilters = computed(() => filterEstado.value !== 'all')

const tableItems = computed(() => {
  if (!filterProveedor.value) return []
  let result = proveedorItems.value
  if (filterEstado.value !== 'all') {
    result = result.filter((i) => i.estado === filterEstado.value)
  }
  return result
})

const estadoOptions = [
  { value: 'all', title: 'Todos' },
  { value: 'BORRADOR', title: 'Borrador' },
  { value: 'APROBADA', title: 'Aprobada' },
  { value: 'CANCELADA', title: 'Cancelada' },
]

const confirmDialogConfig = computed(() => {
  const codigo = actionTarget.value?.codigo ?? ''
  if (confirmAction.value === 'cancel') {
    return {
      title: 'Cancelar orden de compra',
      message: `¿Cancelar la orden ${codigo}? Quedará marcada como cancelada.`,
      confirmText: 'Sí, cancelar',
      confirmColor: 'warning',
      icon: 'mdi-cancel',
      iconColor: 'warning',
    }
  }
  return {
    title: 'Eliminar orden de compra',
    message: `¿Eliminar la orden ${codigo}? Solo aplica a borradores y no se puede deshacer.`,
    confirmText: 'Sí, eliminar',
    confirmColor: 'error',
    icon: 'mdi-delete-outline',
    iconColor: 'error',
  }
})

const totalOrden = computed(() =>
  detalles.value.reduce((acc, d) => {
    if (!d.cantidad || !d.precio_unitario) return acc
    return acc + Number(d.cantidad) * Number(d.precio_unitario)
  }, 0),
)

const headers = [
  { title: 'Número', key: 'codigo', width: 100 },
  { title: 'Fecha', key: 'fecha', width: 96 },
  { title: 'Estado', key: 'estado', width: 96, sortable: false },
  { title: 'Total', key: 'total', align: 'end' as const, width: 108 },
  { title: '', key: 'actions', sortable: false, align: 'end' as const, width: 52 },
]

function formatFecha(value?: string | null) {
  if (!value) return '—'
  const [y, m, d] = value.slice(0, 10).split('-')
  if (!y || !m || !d) return value
  return `${d}/${m}/${y}`
}

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
  form.fecha = new Date().toISOString().slice(0, 10)
  form.observacion = ''
  editingProveedorId.value = null
  detalles.value = [{ key: nextRowKey.value++, producto_id: null, cantidad: null, precio_unitario: null }]
}

function clearFilters() {
  filterEstado.value = 'all'
}

function validateDetalles(): boolean {
  const lineas = detalles.value.filter((d) => d.producto_id)
  if (!lineas.length) {
    appStore.showError('Agregue al menos un producto')
    return false
  }
  for (const d of lineas) {
    if (d.cantidad == null || d.precio_unitario == null) {
      appStore.showError('Complete cantidad y costo en todas las líneas')
      return false
    }
    if (Number(d.cantidad) <= 0) {
      appStore.showError('La cantidad debe ser mayor a 0')
      return false
    }
    if (Number(d.precio_unitario) < 0) {
      appStore.showError('El costo no puede ser negativo')
      return false
    }
  }
  return true
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
  if (!filterProveedor.value) {
    appStore.showError('Seleccione un proveedor para crear una orden')
    return
  }
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
  editingProveedorId.value = item.proveedor_id
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
  const proveedorId = dialogProveedorId.value
  if (!validation?.valid) return
  if (!proveedorId) {
    appStore.showError('Seleccione un proveedor')
    return
  }
  if (!validateDetalles()) return

  const lineas = detalles.value.filter(
    (d) =>
      d.producto_id &&
      d.cantidad != null &&
      d.precio_unitario != null &&
      Number(d.cantidad) > 0 &&
      Number(d.precio_unitario) >= 0,
  )
  if (!lineas.length) {
    appStore.showError('Agregue al menos un detalle válido')
    return
  }

  const payload: OrdenCompraCreate = {
    proveedor_id: proveedorId,
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
  actingId.value = item.id
  acting.value = true
  try {
    await comprasService.aprobarOrdenCompra(item.id)
    appStore.showSuccess('Orden aprobada')
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    acting.value = false
    actingId.value = null
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
  <div class="ordenes-page">
    <PageHeader
      title="Órdenes de Compra"
      subtitle="Proveedor → Orden → Recepción de mercancía"
      icon="mdi-cart-arrow-down"
    >
      <template #actions>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="loading"
          @click="loadData"
        >
          Actualizar
        </v-btn>
        <v-btn
          color="primary"
          size="small"
          prepend-icon="mdi-plus"
          :disabled="!filterProveedor"
          @click="openCreate"
        >
          Nueva orden
        </v-btn>
      </template>
    </PageHeader>

    <div class="proveedor-gate">
      <v-select
        v-model="filterProveedor"
        :items="proveedores"
        item-title="nombre"
        item-value="id"
        label="Proveedor *"
        hide-details
        density="compact"
        prepend-inner-icon="mdi-truck-outline"
        placeholder="Seleccione un proveedor para continuar"
        class="proveedor-gate__select"
      />
      <p v-if="!filterProveedor" class="proveedor-gate__hint">
        <v-icon icon="mdi-information-outline" size="14" class="mr-1" />
        Seleccione un proveedor para ver y gestionar sus órdenes de compra.
      </p>
      <p v-else class="proveedor-gate__active">
        <v-icon icon="mdi-check-circle-outline" size="14" class="mr-1" />
        {{ proveedorSeleccionado?.nombre }}
      </p>
    </div>

    <template v-if="filterProveedor">
      <div class="stats-row">
        <div class="stat-pill">
          <span class="stat-pill__value">{{ stats.total }}</span>
          <span class="stat-pill__label">Total</span>
        </div>
        <div class="stat-pill" :class="{ 'stat-pill--muted': stats.borradores === 0 }">
          <span class="stat-pill__value">{{ stats.borradores }}</span>
          <span class="stat-pill__label">Borradores</span>
        </div>
        <div class="stat-pill stat-pill--ok">
          <span class="stat-pill__value">{{ stats.aprobadas }}</span>
          <span class="stat-pill__label">Aprobadas</span>
        </div>
        <div class="stat-pill stat-pill--money">
          <span class="stat-pill__value">{{ formatMoney(stats.montoAprobado) }}</span>
          <span class="stat-pill__label">Monto aprobado</span>
        </div>
      </div>

      <div class="filters-panel">
        <div class="filters-bar">
          <v-select
            v-model="filterEstado"
            :items="estadoOptions"
            item-title="title"
            item-value="value"
            label="Estado"
            hide-details
            density="compact"
            prepend-inner-icon="mdi-filter-variant"
            class="filters-bar__field filters-bar__field--estado"
          />
          <v-btn
            v-if="hasFilters"
            size="small"
            variant="text"
            prepend-icon="mdi-filter-off-outline"
            class="filters-bar__clear"
            @click="clearFilters"
          >
            Limpiar estado
          </v-btn>
        </div>
      </div>

      <BaseDataTable
        v-model:search="search"
        :items="tableItems as Record<string, unknown>[]"
        :headers="headers"
        :loading="loading"
        title="Listado"
        :subtitle="`Órdenes de ${proveedorSeleccionado?.nombre ?? ''}`"
        search-label="Buscar número o estado..."
        empty-icon="mdi-cart-off"
        empty-title="Sin órdenes"
        empty-subtitle="Crea la primera orden de compra para este proveedor."
      >
        <template #item.codigo="{ value }">
          <span class="code-badge">{{ value }}</span>
        </template>

        <template #item.fecha="{ value }">
          <span class="text-caption">{{ formatFecha(value) }}</span>
        </template>

        <template #item.total="{ value }">
          <span class="money-cell">{{ formatMoney(value) }}</span>
        </template>

        <template #item.estado="{ value }">
          <v-chip :color="ESTADO_COMPRA_COLORS[value] ?? 'default'" size="x-small" variant="tonal" label>
            {{ value }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <v-menu location="bottom end">
            <template #activator="{ props: menuProps }">
              <v-btn
                v-bind="menuProps"
                icon="mdi-dots-vertical"
                size="x-small"
                variant="text"
                aria-label="Acciones"
              />
            </template>
            <v-list density="compact" min-width="160">
              <v-list-item
                prepend-icon="mdi-eye-outline"
                title="Ver detalle"
                @click="openDetail(item as OrdenCompra)"
              />
              <v-list-item
                v-if="item.estado === 'BORRADOR'"
                prepend-icon="mdi-pencil-outline"
                title="Editar"
                @click="openEdit(item as OrdenCompra)"
              />
              <v-list-item
                v-if="item.estado === 'BORRADOR'"
                prepend-icon="mdi-check-circle-outline"
                title="Aprobar"
                :disabled="acting && actingId === item.id"
                @click="aprobar(item as OrdenCompra)"
              />
              <v-list-item
                v-if="['BORRADOR', 'APROBADA'].includes(item.estado)"
                prepend-icon="mdi-cancel"
                title="Cancelar"
                base-color="warning"
                @click="openCancel(item as OrdenCompra)"
              />
              <v-list-item
                v-if="item.estado === 'BORRADOR'"
                prepend-icon="mdi-delete-outline"
                title="Eliminar"
                base-color="error"
                @click="openDelete(item as OrdenCompra)"
              />
            </v-list>
          </v-menu>
        </template>
      </BaseDataTable>
    </template>

    <v-card v-else class="empty-proveedor" border elevation="0">
      <div class="empty-proveedor__content">
        <v-icon icon="mdi-truck-outline" size="48" color="grey-lighten-1" />
        <p class="empty-proveedor__title">Seleccione un proveedor</p>
        <p class="empty-proveedor__sub">Las órdenes se filtrarán automáticamente por el proveedor elegido.</p>
      </div>
    </v-card>
  </div>

  <v-dialog v-model="dialog" max-width="760" persistent scrollable>
    <v-card border elevation="0">
      <v-card-title class="dialog-title pa-4 pb-2">
        <v-avatar color="primary" variant="tonal" size="36" rounded="md">
          <v-icon :icon="editingId ? 'mdi-pencil-outline' : 'mdi-cart-plus'" size="18" />
        </v-avatar>
        <span>{{ editingId ? 'Editar orden' : 'Nueva orden de compra' }}</span>
      </v-card-title>

      <v-card-text class="pa-4 pt-2">
        <v-form ref="formRef">
          <div v-if="dialogProveedorNombre" class="form-proveedor">
            <v-icon icon="mdi-truck-outline" size="16" class="form-proveedor__icon" />
            <span class="form-proveedor__label">Proveedor</span>
            <span class="form-proveedor__name">{{ dialogProveedorNombre }}</span>
          </div>
          <v-alert
            v-else
            type="info"
            variant="tonal"
            density="compact"
            class="mb-3"
          >
            Seleccione un proveedor arriba para continuar.
          </v-alert>

          <v-row dense>
            <v-col cols="12" sm="5">
              <v-text-field
                v-model="form.fecha"
                label="Fecha"
                type="date"
                density="compact"
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col cols="12" sm="7">
              <v-text-field
                v-model="form.observacion"
                label="Observación"
                density="compact"
                hide-details
                prepend-inner-icon="mdi-note-text-outline"
                placeholder="Opcional"
              />
            </v-col>
          </v-row>

          <div class="lines-section">
            <div class="lines-section__header">
              <span class="lines-section__title">Detalles</span>
              <v-btn size="x-small" variant="tonal" prepend-icon="mdi-plus" @click="addLine">
                Línea
              </v-btn>
            </div>

            <v-alert
              v-if="!productos.length"
              type="warning"
              variant="tonal"
              density="compact"
              class="mb-2"
            >
              No hay productos activos en catálogos.
            </v-alert>

            <div v-for="row in detalles" :key="row.key" class="line-row">
              <v-row dense align="center">
                <v-col cols="12" sm="5">
                  <v-select
                    v-model="row.producto_id"
                    :items="productosDisponibles(row.producto_id)"
                    item-title="nombre"
                    item-value="id"
                    label="Producto"
                    density="compact"
                    :rules="[requiredRule]"
                  />
                </v-col>
                <v-col cols="4" sm="2">
                  <v-text-field
                    v-model.number="row.cantidad"
                    label="Cant."
                    type="number"
                    min="0.01"
                    step="0.01"
                    density="compact"
                    :rules="[requiredRule, positiveNumberRule]"
                  />
                </v-col>
                <v-col cols="4" sm="2">
                  <v-text-field
                    v-model.number="row.precio_unitario"
                    label="Costo"
                    type="number"
                    min="0"
                    step="0.01"
                    density="compact"
                    :rules="[requiredRule, nonNegativeRule]"
                  />
                </v-col>
                <v-col cols="3" sm="2" class="line-row__subtotal">
                  {{ formatMoney(lineSubtotal(row)) }}
                </v-col>
                <v-col cols="1" sm="1" class="text-end">
                  <v-btn
                    icon="mdi-close"
                    size="x-small"
                    variant="text"
                    color="error"
                    :disabled="detalles.length <= 1"
                    @click="removeLine(row.key)"
                  />
                </v-col>
              </v-row>
            </div>

            <div class="lines-total">
              <span>Total</span>
              <strong>{{ formatMoney(totalOrden) }}</strong>
            </div>
          </div>
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" size="small" @click="dialog = false">Cancelar</v-btn>
        <v-btn color="primary" size="small" variant="flat" :loading="saving" @click="saveItem">
          Guardar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="detailDialog" max-width="640">
    <v-card v-if="detailItem" border elevation="0">
      <v-card-title class="dialog-title pa-4 pb-2">
        <v-avatar color="primary" variant="tonal" size="36" rounded="md">
          <v-icon icon="mdi-file-document-outline" size="18" />
        </v-avatar>
        <div class="dialog-title__text">
          <span>Orden {{ detailItem.codigo }}</span>
          <v-chip
            :color="ESTADO_COMPRA_COLORS[detailItem.estado] ?? 'default'"
            size="x-small"
            variant="tonal"
            label
            class="mt-1"
          >
            {{ detailItem.estado }}
          </v-chip>
        </div>
      </v-card-title>

      <v-card-text class="pa-4 pt-2">
        <div class="detail-meta">
          <div class="detail-meta__item">
            <v-icon icon="mdi-truck-outline" size="14" class="detail-meta__icon" />
            <span>{{ proveedorMap[detailItem.proveedor_id] }}</span>
          </div>
          <div class="detail-meta__item">
            <v-icon icon="mdi-calendar-outline" size="14" class="detail-meta__icon" />
            <span>{{ formatFecha(detailItem.fecha) }}</span>
          </div>
          <div class="detail-meta__item detail-meta__item--total">
            <span>Total</span>
            <strong>{{ formatMoney(detailItem.total) }}</strong>
          </div>
        </div>

        <v-table density="compact" class="detail-table mt-3">
          <thead>
            <tr>
              <th>Producto</th>
              <th class="text-end">Cant.</th>
              <th class="text-end">Costo</th>
              <th class="text-end">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in detailItem.detalles" :key="d.id">
              <td class="detail-table__product">
                {{ d.producto_nombre ?? productoMap[d.producto_id] ?? d.producto_id }}
              </td>
              <td class="text-end">{{ d.cantidad }}</td>
              <td class="text-end">{{ formatMoney(d.precio_unitario) }}</td>
              <td class="text-end font-weight-medium">
                {{ formatMoney(d.subtotal ?? Number(d.cantidad) * Number(d.precio_unitario)) }}
              </td>
            </tr>
          </tbody>
        </v-table>

        <p v-if="detailItem.observacion" class="detail-obs mt-3">
          <v-icon icon="mdi-note-text-outline" size="14" class="mr-1" />
          {{ detailItem.observacion }}
        </p>
      </v-card-text>

      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" size="small" @click="detailDialog = false">Cerrar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <ConfirmDialog
    v-model="confirmOpen"
    :loading="acting"
    v-bind="confirmDialogConfig"
    @confirm="confirmActionHandler"
  />
</template>

<style scoped>
.ordenes-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.stat-pill {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: #fff;
}

.stat-pill--ok {
  border-color: rgba(var(--v-theme-success), 0.3);
  background: rgba(var(--v-theme-success), 0.05);
}

.stat-pill--ok .stat-pill__value {
  color: rgb(var(--v-theme-success));
}

.stat-pill--money .stat-pill__value {
  font-size: 0.875rem;
}

.stat-pill__value {
  font-size: 1rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  color: rgb(var(--v-theme-on-surface));
}

.stat-pill__label {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.filters-panel {
  padding: 10px 12px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: #fff;
}

.filters-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.filters-bar__field--estado {
  flex: 0 0 180px;
  min-width: 160px;
}

.proveedor-gate {
  padding: 12px 14px;
  border: 1px solid rgba(var(--v-theme-primary), 0.25);
  border-radius: var(--mac-radius-sm);
  background: rgba(var(--v-theme-primary), 0.04);
}

.proveedor-gate__select {
  max-width: 420px;
}

.proveedor-gate__hint {
  margin: 8px 0 0;
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.55);
  display: flex;
  align-items: center;
}

.proveedor-gate__active {
  margin: 8px 0 0;
  font-size: var(--mac-text-xs);
  font-weight: 600;
  color: rgb(var(--v-theme-success));
  display: flex;
  align-items: center;
}

.empty-proveedor {
  padding: 48px 24px;
}

.empty-proveedor__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}

.empty-proveedor__title {
  margin: 8px 0 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.75);
}

.empty-proveedor__sub {
  margin: 0;
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.5);
  max-width: 320px;
}

.filters-bar__clear {
  flex-shrink: 0;
}

.filters-bar__field :deep(.v-select__selection-text),
.filters-bar__field :deep(.v-field-label) {
  overflow: visible;
  text-overflow: clip;
  white-space: nowrap;
}

.code-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: var(--mac-text-xs);
  font-weight: 600;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  letter-spacing: 0.02em;
  background: rgba(var(--v-theme-on-surface), 0.06);
  color: rgba(var(--v-theme-on-surface), 0.8);
}

.cell-ellipsis {
  display: block;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-ellipsis--wide {
  max-width: 200px;
}

.money-cell {
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  font-size: 0.8125rem;
}

.dialog-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  font-weight: 600;
}

.dialog-title__text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.form-proveedor {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  padding: 8px 10px;
  border: 1px solid rgba(var(--v-theme-primary), 0.2);
  border-radius: var(--mac-radius-sm);
  background: rgba(var(--v-theme-primary), 0.05);
}

.form-proveedor__icon {
  flex-shrink: 0;
  opacity: 0.7;
  color: rgb(var(--v-theme-primary));
}

.form-proveedor__label {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.form-proveedor__name {
  font-size: 0.8125rem;
  font-weight: 600;
}

.lines-section {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.lines-section__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.lines-section__title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.7);
}

.line-row {
  padding: 6px 0;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}

.line-row:last-of-type {
  border-bottom: none;
}

.line-row__subtotal {
  font-size: var(--mac-text-xs);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  text-align: end;
  color: rgba(var(--v-theme-on-surface), 0.75);
  padding-top: 8px;
}

.lines-total {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(var(--v-theme-on-surface), 0.12);
  font-size: 0.875rem;
}

.lines-total strong {
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  padding: 8px 10px;
  border-radius: var(--mac-radius-sm);
  background: rgba(var(--v-theme-on-surface), 0.04);
}

.detail-meta__item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.75);
}

.detail-meta__item--total {
  margin-left: auto;
  gap: 8px;
}

.detail-meta__item--total strong {
  font-size: 0.875rem;
  font-variant-numeric: tabular-nums;
}

.detail-meta__icon {
  opacity: 0.55;
}

.detail-table :deep(th) {
  font-size: var(--mac-text-xs) !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: rgba(var(--v-theme-on-surface), 0.5) !important;
}

.detail-table__product {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8125rem;
}

.detail-obs {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin: 0;
}

@media (max-width: 600px) {
  .filters-bar__field--estado {
    flex: 1 1 100%;
    min-width: 100%;
    max-width: 100%;
  }

  .proveedor-gate__select {
    max-width: 100%;
  }

  .cell-ellipsis,
  .cell-ellipsis--wide {
    max-width: 100px;
  }

  .detail-meta__item--total {
    margin-left: 0;
    width: 100%;
    justify-content: space-between;
  }
}
</style>
