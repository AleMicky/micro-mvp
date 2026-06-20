<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { companyService } from '@/services/company.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Almacen } from '@/types/inventario.types'
import type { Compania, Sucursal } from '@/types/company.types'

const appStore = useAppStore()

const items = ref<Almacen[]>([])
const sucursales = ref<Sucursal[]>([])
const companias = ref<Compania[]>([])
const loading = ref(false)
const loadingSucursales = ref(false)
const search = ref('')
const filterCompania = ref<number | null>(null)
const filterEstado = ref<'all' | 'activo' | 'inactivo'>('all')
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<Almacen | null>(null)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const defaultForm = () => ({
  codigo: '',
  nombre: '',
  direccion: '',
  sucursal_id: null as number | null,
  activo: true,
})

const form = reactive(defaultForm())

const stats = computed(() => {
  const activos = items.value.filter((i) => i.activo).length
  const conSucursal = items.value.filter((i) => i.sucursal_id).length
  return {
    total: items.value.length,
    activos,
    inactivos: items.value.length - activos,
    conSucursal,
  }
})

const hasFilters = computed(
  () => filterCompania.value !== null || filterEstado.value !== 'all',
)

const companiaFilterOptions = computed(() =>
  companias.value
    .filter((c) => c.activo)
    .map((c) => ({ id: c.id, nombre: c.nombre }))
    .sort((a, b) => a.nombre.localeCompare(b.nombre)),
)

const tableItems = computed(() => {
  let result = items.value
  if (filterCompania.value) {
    result = result.filter((i) => i.compania_id === filterCompania.value)
  }
  if (filterEstado.value === 'activo') {
    result = result.filter((i) => i.activo)
  } else if (filterEstado.value === 'inactivo') {
    result = result.filter((i) => !i.activo)
  }
  return result
})

const estadoOptions = [
  { value: 'all', title: 'Todos' },
  { value: 'activo', title: 'Activos' },
  { value: 'inactivo', title: 'Inactivos' },
]

const headers = [
  { title: 'Código', key: 'codigo', width: 88 },
  { title: 'Almacén', key: 'nombre' },
  { title: 'Sucursal', key: 'sucursal_nombre', width: 140 },
  { title: 'Compañía', key: 'compania_nombre', width: 120 },
  { title: 'Estado', key: 'activo', width: 80, sortable: false },
  { title: '', key: 'actions', sortable: false, align: 'end' as const, width: 52 },
]

const sucursalOptions = computed(() => {
  const companiaPorId = new Map(companias.value.map((c) => [c.id, c.nombre]))
  return sucursales.value
    .filter((s) => s.activo)
    .map((s) => ({
      id: s.id,
      codigo: s.codigo,
      nombre: s.nombre,
      compania_id: s.compania_id,
      compania_nombre: companiaPorId.get(s.compania_id) ?? '—',
      label: `${companiaPorId.get(s.compania_id) ?? '—'} · ${s.nombre}`,
    }))
    .sort((a, b) => {
      const cmp = a.compania_nombre.localeCompare(b.compania_nombre)
      return cmp !== 0 ? cmp : a.nombre.localeCompare(b.nombre)
    })
})

function clearFilters() {
  filterCompania.value = null
  filterEstado.value = 'all'
}

async function loadSucursales() {
  loadingSucursales.value = true
  try {
    const [sucursalesRes, companiasRes] = await Promise.all([
      companyService.getSucursales(),
      companyService.getCompanias(),
    ])
    sucursales.value = sucursalesRes.data
    companias.value = companiasRes.data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loadingSucursales.value = false
  }
}

async function loadData() {
  loading.value = true
  try {
    const { data } = await inventarioService.getAlmacenes()
    items.value = data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, defaultForm())
  dialog.value = true
}

function openEdit(item: Almacen) {
  editingId.value = item.id
  Object.assign(form, {
    codigo: item.codigo,
    nombre: item.nombre,
    direccion: item.direccion ?? '',
    sucursal_id: item.sucursal_id ?? null,
    activo: item.activo,
  })
  dialog.value = true
}

function openDelete(item: Almacen) {
  deleteTarget.value = item
  confirmOpen.value = true
}

async function saveItem() {
  if (!(await formRef.value?.validate())?.valid) return
  saving.value = true
  try {
    const payload = {
      codigo: form.codigo.trim(),
      nombre: form.nombre.trim(),
      direccion: form.direccion.trim() || null,
      sucursal_id: form.sucursal_id,
      activo: form.activo,
    }
    if (editingId.value) {
      await inventarioService.updateAlmacen(editingId.value, payload)
      appStore.showSuccess('Almacén actualizado')
    } else {
      await inventarioService.createAlmacen(payload)
      appStore.showSuccess('Almacén creado')
    }
    dialog.value = false
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await inventarioService.deleteAlmacen(deleteTarget.value.id)
    appStore.showSuccess('Almacén eliminado')
    confirmOpen.value = false
    deleteTarget.value = null
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadData(), loadSucursales()])
})
</script>

<template>
  <div class="almacenes-page">
    <PageHeader
      title="Almacenes"
      subtitle="Ubicaciones físicas para existencias e inventario"
      icon="mdi-warehouse"
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
        <v-btn color="primary" size="small" prepend-icon="mdi-plus" @click="openCreate">
          Nuevo
        </v-btn>
      </template>
    </PageHeader>

    <div class="stats-row">
      <div class="stat-pill">
        <span class="stat-pill__value">{{ stats.total }}</span>
        <span class="stat-pill__label">Total</span>
      </div>
      <div class="stat-pill stat-pill--ok">
        <span class="stat-pill__value">{{ stats.activos }}</span>
        <span class="stat-pill__label">Activos</span>
      </div>
      <div class="stat-pill" :class="{ 'stat-pill--warn': stats.inactivos > 0 }">
        <span class="stat-pill__value">{{ stats.inactivos }}</span>
        <span class="stat-pill__label">Inactivos</span>
      </div>
      <div class="stat-pill">
        <span class="stat-pill__value">{{ stats.conSucursal }}</span>
        <span class="stat-pill__label">Con sucursal</span>
      </div>
    </div>

    <div class="filters-panel">
      <div class="filters-bar">
        <v-select
          v-model="filterCompania"
          :items="companiaFilterOptions"
          item-title="nombre"
          item-value="id"
          label="Compañía"
          clearable
          hide-details
          density="compact"
          prepend-inner-icon="mdi-domain"
          class="filters-bar__field filters-bar__field--compania"
        />
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
          Limpiar
        </v-btn>
      </div>
    </div>

    <BaseDataTable
      v-model:search="search"
      :items="tableItems as Record<string, unknown>[]"
      :headers="headers"
      :loading="loading"
      title="Listado"
      subtitle="Almacenes registrados"
      search-label="Buscar código, nombre o sucursal..."
      empty-icon="mdi-warehouse-off"
      empty-title="Sin almacenes"
      empty-subtitle="Crea el primer almacén para registrar existencias."
    >
      <template #item.codigo="{ value }">
        <span class="code-badge">{{ value }}</span>
      </template>

      <template #item.nombre="{ item }">
        <div class="name-cell">
          <span class="name-cell__title cell-ellipsis" :title="item.nombre">
            {{ item.nombre }}
          </span>
          <span
            v-if="item.direccion"
            class="name-cell__sub cell-ellipsis"
            :title="item.direccion"
          >
            {{ item.direccion }}
          </span>
        </div>
      </template>

      <template #item.sucursal_nombre="{ value }">
        <span v-if="value" class="cell-ellipsis" :title="value">
          <v-icon icon="mdi-store-marker-outline" size="12" class="mr-1 text-medium-emphasis" />
          {{ value }}
        </span>
        <span v-else class="text-caption text-medium-emphasis">Sin asignar</span>
      </template>

      <template #item.compania_nombre="{ value }">
        <span class="cell-ellipsis text-caption" :title="value || undefined">
          {{ value || '—' }}
        </span>
      </template>

      <template #item.activo="{ value }">
        <v-chip :color="value ? 'success' : 'error'" size="x-small" variant="tonal" label>
          {{ value ? 'Activo' : 'Inactivo' }}
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
          <v-list density="compact" min-width="140">
            <v-list-item
              prepend-icon="mdi-pencil-outline"
              title="Editar"
              @click="openEdit(item as Almacen)"
            />
            <v-list-item
              prepend-icon="mdi-delete-outline"
              title="Eliminar"
              base-color="error"
              @click="openDelete(item as Almacen)"
            />
          </v-list>
        </v-menu>
      </template>
    </BaseDataTable>
  </div>

  <v-dialog v-model="dialog" max-width="520" persistent>
    <v-card border elevation="0">
      <v-card-title class="dialog-title pa-4 pb-2">
        <v-avatar color="primary" variant="tonal" size="36" rounded="md">
          <v-icon :icon="editingId ? 'mdi-pencil-outline' : 'mdi-warehouse'" size="18" />
        </v-avatar>
        <span>{{ editingId ? 'Editar almacén' : 'Nuevo almacén' }}</span>
      </v-card-title>

      <v-card-text class="pa-4 pt-2">
        <v-form ref="formRef">
          <v-row dense>
            <v-col cols="12" sm="5">
              <v-text-field
                v-model="form.codigo"
                label="Código"
                density="compact"
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col cols="12" sm="7">
              <v-text-field
                v-model="form.nombre"
                label="Nombre"
                density="compact"
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col cols="12">
              <v-autocomplete
                v-model="form.sucursal_id"
                :items="sucursalOptions"
                item-title="label"
                item-value="id"
                label="Sucursal"
                clearable
                density="compact"
                hide-details
                :loading="loadingSucursales"
                prepend-inner-icon="mdi-store-marker-outline"
                placeholder="Opcional"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.direccion"
                label="Dirección"
                density="compact"
                hide-details
                prepend-inner-icon="mdi-map-marker-outline"
              />
            </v-col>
            <v-col cols="12">
              <v-switch
                v-model="form.activo"
                label="Activo"
                color="success"
                density="compact"
                hide-details
              />
            </v-col>
          </v-row>
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

  <ConfirmDialog
    v-model="confirmOpen"
    :loading="deleting"
    :message="`¿Eliminar el almacén «${deleteTarget?.nombre}»?`"
    @confirm="confirmDelete"
  />
</template>

<style scoped>
.almacenes-page {
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

.stat-pill--warn {
  border-color: rgba(var(--v-theme-warning), 0.35);
  background: rgba(var(--v-theme-warning), 0.06);
}

.stat-pill__value {
  font-size: 1rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  color: rgb(var(--v-theme-on-surface));
}

.stat-pill--ok .stat-pill__value {
  color: rgb(var(--v-theme-success));
}

.stat-pill--warn .stat-pill__value {
  color: rgb(var(--v-theme-warning));
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

.filters-bar__field--compania {
  flex: 1 1 240px;
  min-width: 220px;
  max-width: 420px;
}

.filters-bar__field--estado {
  flex: 0 0 160px;
  min-width: 150px;
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

.name-cell {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
  max-width: 220px;
}

.name-cell__title {
  font-weight: 500;
  font-size: 0.8125rem;
}

.name-cell__sub {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.cell-ellipsis {
  display: block;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  font-weight: 600;
}

@media (max-width: 600px) {
  .filters-bar__field--compania,
  .filters-bar__field--estado {
    flex: 1 1 100%;
    min-width: 100%;
    max-width: 100%;
  }

  .name-cell {
    max-width: 140px;
  }

  .cell-ellipsis {
    max-width: 100px;
  }
}
</style>
