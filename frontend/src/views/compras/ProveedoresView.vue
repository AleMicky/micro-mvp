<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { comprasService } from '@/services/compras.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Proveedor } from '@/types/compras.types'

const appStore = useAppStore()
const items = ref<Proveedor[]>([])
const loading = ref(false)
const search = ref('')
const filterEstado = ref<'all' | 'activo' | 'inactivo'>('all')
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<Proveedor | null>(null)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const defaultForm = () => ({
  codigo: '',
  nombre: '',
  rfc: '',
  email: '',
  telefono: '',
  direccion: '',
  activo: true,
})
const form = reactive(defaultForm())

const stats = computed(() => {
  const activos = items.value.filter((i) => i.activo).length
  const conContacto = items.value.filter((i) => i.email || i.telefono).length
  return {
    total: items.value.length,
    activos,
    inactivos: items.value.length - activos,
    conContacto,
  }
})

const hasFilters = computed(() => filterEstado.value !== 'all')

const tableItems = computed(() => {
  if (filterEstado.value === 'activo') return items.value.filter((i) => i.activo)
  if (filterEstado.value === 'inactivo') return items.value.filter((i) => !i.activo)
  return items.value
})

const estadoOptions = [
  { value: 'all', title: 'Todos' },
  { value: 'activo', title: 'Activos' },
  { value: 'inactivo', title: 'Inactivos' },
]

const headers = [
  { title: 'Código', key: 'codigo', width: 88 },
  { title: 'Proveedor', key: 'nombre' },
  { title: 'NIT', key: 'rfc', width: 100 },
  { title: 'Contacto', key: 'contacto', sortable: false, width: 168 },
  { title: 'Estado', key: 'activo', width: 80, sortable: false },
  { title: '', key: 'actions', sortable: false, align: 'end' as const, width: 52 },
]

function clearFilters() {
  filterEstado.value = 'all'
}

async function loadData() {
  loading.value = true
  try {
    const { data } = await comprasService.getProveedores()
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

function openEdit(item: Proveedor) {
  editingId.value = item.id
  Object.assign(form, {
    codigo: item.codigo,
    nombre: item.nombre,
    rfc: item.rfc ?? '',
    email: item.email ?? '',
    telefono: item.telefono ?? '',
    direccion: item.direccion ?? '',
    activo: item.activo,
  })
  dialog.value = true
}

function openDelete(item: Proveedor) {
  deleteTarget.value = item
  confirmOpen.value = true
}

async function saveItem() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid) return
  saving.value = true
  try {
    const payload = {
      codigo: form.codigo.trim(),
      nombre: form.nombre.trim(),
      rfc: form.rfc || null,
      email: form.email || null,
      telefono: form.telefono || null,
      direccion: form.direccion || null,
      activo: form.activo,
    }
    if (editingId.value) {
      await comprasService.updateProveedor(editingId.value, payload)
      appStore.showSuccess('Proveedor actualizado')
    } else {
      await comprasService.createProveedor(payload)
      appStore.showSuccess('Proveedor creado')
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
    await comprasService.deleteProveedor(deleteTarget.value.id)
    appStore.showSuccess('Proveedor desactivado')
    confirmOpen.value = false
    deleteTarget.value = null
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    deleting.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div class="proveedores-page">
    <PageHeader
      title="Proveedores"
      subtitle="Catálogo de proveedores para órdenes de compra"
      icon="mdi-truck-outline"
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
        <span class="stat-pill__value">{{ stats.conContacto }}</span>
        <span class="stat-pill__label">Con contacto</span>
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
      subtitle="Proveedores registrados"
      search-label="Buscar código, nombre, NIT o contacto..."
      empty-icon="mdi-truck-off-outline"
      empty-title="Sin proveedores"
      empty-subtitle="Registra el primer proveedor para crear órdenes de compra."
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

      <template #item.rfc="{ value }">
        <span v-if="value" class="text-caption font-weight-medium">{{ value }}</span>
        <span v-else class="text-caption text-medium-emphasis">—</span>
      </template>

      <template #item.contacto="{ item }">
        <div v-if="item.telefono || item.email" class="contact-cell">
          <span v-if="item.telefono" class="contact-cell__line cell-ellipsis" :title="item.telefono">
            <v-icon icon="mdi-phone-outline" size="12" class="contact-cell__icon" />
            {{ item.telefono }}
          </span>
          <span v-if="item.email" class="contact-cell__line cell-ellipsis" :title="item.email">
            <v-icon icon="mdi-email-outline" size="12" class="contact-cell__icon" />
            {{ item.email }}
          </span>
        </div>
        <span v-else class="text-caption text-medium-emphasis">Sin contacto</span>
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
              @click="openEdit(item as Proveedor)"
            />
            <v-list-item
              prepend-icon="mdi-archive-off-outline"
              title="Desactivar"
              base-color="error"
              :disabled="!(item as Proveedor).activo"
              @click="openDelete(item as Proveedor)"
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
          <v-icon :icon="editingId ? 'mdi-pencil-outline' : 'mdi-truck-outline'" size="18" />
        </v-avatar>
        <span>{{ editingId ? 'Editar proveedor' : 'Nuevo proveedor' }}</span>
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
                label="Razón social"
                density="compact"
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.rfc"
                label="NIT"
                density="compact"
                hide-details
                prepend-inner-icon="mdi-card-account-details-outline"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.telefono"
                label="Teléfono"
                density="compact"
                hide-details
                prepend-inner-icon="mdi-phone-outline"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.email"
                label="Correo"
                density="compact"
                hide-details
                prepend-inner-icon="mdi-email-outline"
                type="email"
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
    title="Desactivar proveedor"
    :message="`¿Desactivar el proveedor «${deleteTarget?.nombre}»? No se podrá usar en nuevas órdenes.`"
    confirm-text="Sí, desactivar"
    confirm-color="warning"
    icon="mdi-archive-off-outline"
    icon-color="warning"
    @confirm="confirmDelete"
  />
</template>

<style scoped>
.proveedores-page {
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
  max-width: 240px;
}

.name-cell__title {
  font-weight: 500;
  font-size: 0.8125rem;
}

.name-cell__sub {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.contact-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  max-width: 160px;
}

.contact-cell__line {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.75);
}

.contact-cell__icon {
  flex-shrink: 0;
  opacity: 0.55;
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
  .filters-bar__field--estado {
    flex: 1 1 100%;
    min-width: 100%;
    max-width: 100%;
  }

  .name-cell,
  .contact-cell {
    max-width: 120px;
  }

  .cell-ellipsis {
    max-width: 100px;
  }
}
</style>
