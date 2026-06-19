<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import PageHeader from '@/components/PageHeader.vue'
import { companyService } from '@/services/company.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Compania, Sucursal } from '@/types/company.types'

const appStore = useAppStore()

const empresas = ref<Compania[]>([])
const sucursales = ref<Sucursal[]>([])
const selectedEmpresaId = ref<number | null>(null)
const loadingEmpresas = ref(false)
const loadingSucursales = ref(false)
const isDetailTransition = ref(false)
const searchEmpresas = ref('')
const searchSucursales = ref('')

const empresaDialog = ref(false)
const sucursalDialog = ref(false)
const confirmEmpresaOpen = ref(false)
const confirmSucursalOpen = ref(false)
const savingEmpresa = ref(false)
const savingSucursal = ref(false)
const deletingEmpresa = ref(false)
const deletingSucursal = ref(false)
const editingEmpresaId = ref<number | null>(null)
const editingSucursalId = ref<number | null>(null)
const deleteEmpresaTarget = ref<Compania | null>(null)
const deleteSucursalTarget = ref<Sucursal | null>(null)
const empresaFormRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const sucursalFormRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const defaultEmpresaForm = () => ({
  codigo: '',
  nombre: '',
  nit: '',
  direccion: '',
  telefono: '',
  activo: true,
})
const defaultSucursalForm = () => ({
  codigo: '',
  nombre: '',
  ciudad_id: 1,
  direccion: '',
  activo: true,
})

const empresaForm = reactive(defaultEmpresaForm())
const sucursalForm = reactive(defaultSucursalForm())

const selectedEmpresa = computed(() =>
  empresas.value.find((e) => e.id === selectedEmpresaId.value) ?? null,
)

const isDetailLoading = computed(() => isDetailTransition.value && !!selectedEmpresaId.value)

const filteredEmpresas = computed(() => {
  const term = searchEmpresas.value.trim().toLowerCase()
  if (!term) return empresas.value
  return empresas.value.filter((e) =>
    [e.codigo, e.nombre, e.nit].some((v) => v?.toLowerCase().includes(term)),
  )
})

const sucursalHeaders = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Dirección', key: 'direccion' },
  { title: 'Estado', key: 'activo' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 120 },
]

function ensureSelection() {
  if (!empresas.value.length) {
    selectedEmpresaId.value = null
    return
  }
  const stillExists = empresas.value.some((e) => e.id === selectedEmpresaId.value)
  if (!stillExists) {
    selectedEmpresaId.value = empresas.value[0].id
  }
}

async function loadEmpresas() {
  loadingEmpresas.value = true
  try {
    empresas.value = (await companyService.getCompanias()).data
    ensureSelection()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loadingEmpresas.value = false
  }
}

async function loadSucursales(clearFirst = false) {
  if (!selectedEmpresaId.value) {
    sucursales.value = []
    return
  }
  loadingSucursales.value = true
  if (clearFirst) sucursales.value = []
  try {
    sucursales.value = (await companyService.getSucursalesByCompania(selectedEmpresaId.value)).data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loadingSucursales.value = false
  }
}

function selectEmpresa(empresa: Compania) {
  if (selectedEmpresaId.value === empresa.id) return
  selectedEmpresaId.value = empresa.id
}

function openCreateEmpresa() {
  editingEmpresaId.value = null
  Object.assign(empresaForm, defaultEmpresaForm())
  empresaDialog.value = true
}

function openEditEmpresa(item?: Compania) {
  const target = item ?? selectedEmpresa.value
  if (!target) return
  editingEmpresaId.value = target.id
  Object.assign(empresaForm, {
    codigo: target.codigo,
    nombre: target.nombre,
    nit: target.nit ?? '',
    direccion: target.direccion ?? '',
    telefono: target.telefono ?? '',
    activo: target.activo,
  })
  empresaDialog.value = true
}

function openDeleteEmpresa(item?: Compania) {
  const target = item ?? selectedEmpresa.value
  if (!target) return
  deleteEmpresaTarget.value = target
  confirmEmpresaOpen.value = true
}

async function saveEmpresa() {
  if (!(await empresaFormRef.value?.validate())?.valid) return
  const wasCreate = !editingEmpresaId.value
  savingEmpresa.value = true
  try {
    const payload = {
      codigo: empresaForm.codigo.trim(),
      nombre: empresaForm.nombre.trim(),
      nit: empresaForm.nit || null,
      direccion: empresaForm.direccion || null,
      telefono: empresaForm.telefono || null,
      activo: empresaForm.activo,
    }
    if (editingEmpresaId.value) {
      await companyService.updateCompania(editingEmpresaId.value, payload)
      appStore.showSuccess('Empresa actualizada')
    } else {
      const { data } = await companyService.createCompania(payload)
      selectedEmpresaId.value = data.id
      appStore.showSuccess('Empresa creada')
    }
    empresaDialog.value = false
    await loadEmpresas()
    if (wasCreate && selectedEmpresaId.value) {
      isDetailTransition.value = true
      await loadSucursales(true)
      isDetailTransition.value = false
    }
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    savingEmpresa.value = false
  }
}

async function confirmDeleteEmpresa() {
  if (!deleteEmpresaTarget.value) return
  deletingEmpresa.value = true
  try {
    const deletedId = deleteEmpresaTarget.value.id
    await companyService.deleteCompania(deletedId)
    if (selectedEmpresaId.value === deletedId) {
      selectedEmpresaId.value = null
    }
    appStore.showSuccess('Empresa eliminada')
    confirmEmpresaOpen.value = false
    await loadEmpresas()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    deletingEmpresa.value = false
  }
}

function openCreateSucursal() {
  if (!selectedEmpresaId.value) return
  editingSucursalId.value = null
  Object.assign(sucursalForm, defaultSucursalForm())
  sucursalDialog.value = true
}

function openEditSucursal(item: Sucursal) {
  editingSucursalId.value = item.id
  Object.assign(sucursalForm, {
    codigo: item.codigo,
    nombre: item.nombre,
    ciudad_id: item.ciudad_id,
    direccion: item.direccion ?? '',
    activo: item.activo,
  })
  sucursalDialog.value = true
}

function openDeleteSucursal(item: Sucursal) {
  deleteSucursalTarget.value = item
  confirmSucursalOpen.value = true
}

async function saveSucursal() {
  if (!(await sucursalFormRef.value?.validate())?.valid || !selectedEmpresaId.value) return
  savingSucursal.value = true
  try {
    const payload = {
      codigo: sucursalForm.codigo.trim(),
      nombre: sucursalForm.nombre.trim(),
      compania_id: selectedEmpresaId.value,
      ciudad_id: sucursalForm.ciudad_id,
      direccion: sucursalForm.direccion || null,
      activo: sucursalForm.activo,
    }
    if (editingSucursalId.value) {
      await companyService.updateSucursal(editingSucursalId.value, payload)
      appStore.showSuccess('Sucursal actualizada')
    } else {
      await companyService.createSucursal(payload)
      appStore.showSuccess('Sucursal creada')
    }
    sucursalDialog.value = false
    await loadSucursales()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    savingSucursal.value = false
  }
}

async function confirmDeleteSucursal() {
  if (!deleteSucursalTarget.value) return
  deletingSucursal.value = true
  try {
    await companyService.deleteSucursal(deleteSucursalTarget.value.id)
    appStore.showSuccess('Sucursal eliminada')
    confirmSucursalOpen.value = false
    await loadSucursales()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    deletingSucursal.value = false
  }
}

watch(selectedEmpresaId, async (newId, oldId) => {
  if (newId === oldId || oldId == null) return
  isDetailTransition.value = true
  await loadSucursales(true)
  isDetailTransition.value = false
})

onMounted(async () => {
  isDetailTransition.value = true
  await loadEmpresas()
  if (selectedEmpresaId.value) {
    await loadSucursales(true)
  }
  isDetailTransition.value = false
})
</script>

<template>
  <div>
    <PageHeader title="Empresas" subtitle="Administra empresas y sus sucursales en un solo lugar" icon="mdi-domain">
    
    </PageHeader>

    <v-card class="master-detail" elevation="0" border>
      <v-row no-gutters>
        <!-- Maestro -->
        <v-col cols="12" md="4" lg="3" class="master-panel">
          <div class="master-panel__header pa-4">
            <div class="d-flex align-center justify-space-between mb-1">
              <div>
                <div class="text-subtitle-1 font-weight-bold">Empresas</div>
                <div class="text-caption text-medium-emphasis">{{ empresas.length }} registrada(s)</div>
              </div>
              <v-btn
                icon="mdi-plus"
                size="small"
                color="primary"
                variant="tonal"
                aria-label="Nueva empresa"
                @click="openCreateEmpresa"
              />
            </div>
            <v-text-field
              v-model="searchEmpresas"
              label="Buscar..."
              prepend-inner-icon="mdi-magnify"
              clearable
              hide-details
              density="compact"
              class="mt-2"
              bg-color="surface"
            />
          </div>

          <v-divider />

          <div v-if="loadingEmpresas" class="pa-4">
            <v-skeleton-loader type="list-item-two-line@4" />
          </div>

          <v-list v-else-if="filteredEmpresas.length" nav density="comfortable" class="master-list py-2">
            <v-list-item
              v-for="empresa in filteredEmpresas"
              :key="empresa.id"
              :value="empresa.id"
              :active="selectedEmpresaId === empresa.id"
              rounded="lg"
              class="master-list__item mx-2 mb-1"
              @click="selectEmpresa(empresa)"
            >
              <template #prepend>
                <v-avatar
                  :color="selectedEmpresaId === empresa.id ? 'primary' : 'grey-lighten-3'"
                  size="40"
                  rounded="lg"
                >
                  <v-icon
                    :icon="selectedEmpresaId === empresa.id ? 'mdi-domain' : 'mdi-office-building-outline'"
                    :color="selectedEmpresaId === empresa.id ? 'white' : undefined"
                    size="20"
                  />
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">{{ empresa.nombre }}</v-list-item-title>
              <v-list-item-subtitle>{{ empresa.codigo }}</v-list-item-subtitle>

              <template #append>
                <div class="d-flex align-center ga-1" @click.stop>
                  <v-progress-circular
                    v-if="selectedEmpresaId === empresa.id && loadingSucursales"
                    indeterminate
                    size="16"
                    width="2"
                    color="primary"
                  />
                  <v-chip v-else :color="empresa.activo ? 'success' : 'error'" size="x-small" variant="tonal">
                    {{ empresa.activo ? 'Activa' : 'Inactiva' }}
                  </v-chip>
                  <v-menu location="bottom end">
                    <template #activator="{ props: menuProps }">
                      <v-btn
                        v-bind="menuProps"
                        icon="mdi-dots-vertical"
                        size="x-small"
                        variant="text"
                        aria-label="Acciones de empresa"
                      />
                    </template>
                    <v-list density="compact" min-width="160">
                      <v-list-item prepend-icon="mdi-pencil-outline" title="Editar" @click="openEditEmpresa(empresa)" />
                      <v-list-item
                        prepend-icon="mdi-delete-outline"
                        title="Eliminar"
                        base-color="error"
                        @click="openDeleteEmpresa(empresa)"
                      />
                    </v-list>
                  </v-menu>
                </div>
              </template>
            </v-list-item>
          </v-list>

          <div v-else class="empty-master pa-8 text-center">
            <v-icon icon="mdi-domain-off" size="48" color="grey-lighten-1" class="mb-3" />
            <div class="text-subtitle-2 font-weight-medium">Sin empresas</div>
            <div class="text-body-2 text-medium-emphasis mt-1 mb-4">
              {{ searchEmpresas ? 'No hay coincidencias.' : 'Crea la primera empresa para comenzar.' }}
            </div>
            <v-btn v-if="!searchEmpresas" color="primary" size="small" prepend-icon="mdi-plus" @click="openCreateEmpresa">
              Nueva empresa
            </v-btn>
          </div>
        </v-col>

        <v-divider vertical class="d-none d-md-flex" />

        <!-- Detalle -->
        <v-col cols="12" md="8" lg="9" class="detail-panel">
          <template v-if="selectedEmpresa">
            <v-progress-linear
              v-if="isDetailLoading"
              indeterminate
              color="primary"
              height="3"
              class="detail-progress"
            />

            <div :key="selectedEmpresa.id" class="detail-content">
              <div class="detail-panel__header pa-5">
                <div class="d-flex align-start ga-3">
                  <v-avatar color="primary" size="52" rounded="lg" class="flex-shrink-0">
                    <v-icon icon="mdi-domain" color="white" />
                  </v-avatar>
                  <div class="flex-grow-1 min-w-0">
                    <div class="text-h6 font-weight-bold text-truncate">{{ selectedEmpresa.nombre }}</div>
                    <div class="text-body-2 text-medium-emphasis d-flex flex-wrap ga-2 mt-1">
                      <span><v-icon icon="mdi-barcode" size="14" class="mr-1" />{{ selectedEmpresa.codigo }}</span>
                      <span v-if="selectedEmpresa.nit">
                        <v-icon icon="mdi-card-account-details-outline" size="14" class="mr-1" />NIT {{ selectedEmpresa.nit }}
                      </span>
                      <v-chip :color="selectedEmpresa.activo ? 'success' : 'error'" size="x-small" variant="tonal">
                        {{ selectedEmpresa.activo ? 'Activa' : 'Inactiva' }}
                      </v-chip>
                      <v-skeleton-loader
                        v-if="isDetailLoading"
                        type="chip"
                        width="120"
                        class="detail-chip-skeleton"
                      />
                      <v-chip v-else size="x-small" variant="outlined" prepend-icon="mdi-store-marker-outline">
                        {{ sucursales.length }} sucursal(es)
                      </v-chip>
                    </div>
                  </div>
                </div>

                <div class="detail-toolbar mt-4">
                  <v-btn
                    size="small"
                    variant="tonal"
                    prepend-icon="mdi-pencil-outline"
                    :disabled="isDetailLoading"
                    @click="openEditEmpresa()"
                  >
                    Editar empresa
                  </v-btn>
                  <v-btn
                    size="small"
                    variant="text"
                    color="error"
                    prepend-icon="mdi-delete-outline"
                    :disabled="isDetailLoading"
                    @click="openDeleteEmpresa()"
                  >
                    Eliminar empresa
                  </v-btn>
                </div>
              </div>

              <v-divider />

              <div class="pa-5 pt-0 detail-table-area">
                <div v-if="isDetailLoading" class="detail-skeleton pa-5">
                  <div class="d-flex align-center justify-space-between mb-4">
                    <v-skeleton-loader type="heading" width="180" />
                    <v-skeleton-loader type="button" width="140" />
                  </div>
                  <v-skeleton-loader type="text" width="260" class="mb-4" />
                  <v-skeleton-loader type="table-row@5" />
                </div>

                <v-fade-transition mode="out-in">
                  <BaseDataTable
                    v-if="!isDetailLoading"
                    v-model:search="searchSucursales"
                    :items="sucursales"
                    :headers="sucursalHeaders"
                    :loading="loadingSucursales"
                    title="Sucursales"
                    :subtitle="`Puntos de venta de ${selectedEmpresa.nombre}`"
                    search-label="Buscar sucursal..."
                    empty-icon="mdi-store-off-outline"
                    empty-title="Sin sucursales"
                    empty-subtitle="Esta empresa aún no tiene sucursales."
                  >
                    <template #actions>
                      <v-btn size="small" color="primary" prepend-icon="mdi-plus" @click="openCreateSucursal">
                        Nueva sucursal
                      </v-btn>
                    </template>
                    <template #item.direccion="{ value }">
                      {{ value || '—' }}
                    </template>

                    <template #item.activo="{ value }">
                      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">
                        {{ value ? 'Activa' : 'Inactiva' }}
                      </v-chip>
                    </template>

                    <template #item.actions="{ item }">
                      <v-btn icon="mdi-pencil-outline" size="small" variant="text" @click="openEditSucursal(item)" />
                      <v-btn icon="mdi-delete-outline" size="small" variant="text" color="error" @click="openDeleteSucursal(item)" />
                    </template>
                  </BaseDataTable>
                </v-fade-transition>
              </div>
            </div>
          </template>

          <div v-else class="detail-empty pa-12 text-center">
            <v-icon icon="mdi-cursor-default-click-outline" size="64" color="grey-lighten-1" class="mb-4" />
            <div class="text-h6 font-weight-medium">Selecciona una empresa</div>
            <div class="text-body-2 text-medium-emphasis mt-2 mb-6">
              Elige una empresa del listado o crea una nueva para gestionar sus sucursales.
            </div>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateEmpresa">Nueva empresa</v-btn>
          </div>
        </v-col>
      </v-row>
    </v-card>

    <v-dialog v-model="empresaDialog" max-width="640" persistent>
      <v-card>
        <v-card-title class="pa-5">{{ editingEmpresaId ? 'Editar empresa' : 'Nueva empresa' }}</v-card-title>
        <v-card-text class="pa-5">
          <v-form ref="empresaFormRef">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="empresaForm.codigo" label="Código" :rules="[requiredRule]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="empresaForm.nit" label="NIT" />
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="empresaForm.nombre" label="Nombre" :rules="[requiredRule]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="empresaForm.telefono" label="Teléfono" />
              </v-col>
              <v-col cols="12" sm="6" class="d-flex align-center">
                <v-switch v-model="empresaForm.activo" label="Activa" color="success" hide-details />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5">
          <v-spacer />
          <v-btn variant="text" @click="empresaDialog = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="savingEmpresa" @click="saveEmpresa">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="sucursalDialog" max-width="640" persistent>
      <v-card>
        <v-card-title class="pa-5">{{ editingSucursalId ? 'Editar sucursal' : 'Nueva sucursal' }}</v-card-title>
        <v-card-text class="pa-5">
          <v-alert v-if="selectedEmpresa" type="info" variant="tonal" density="compact" class="mb-4">
            Empresa: <strong>{{ selectedEmpresa.nombre }}</strong>
          </v-alert>
          <v-form ref="sucursalFormRef">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="sucursalForm.codigo" label="Código" :rules="[requiredRule]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="sucursalForm.nombre" label="Nombre" :rules="[requiredRule]" />
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="sucursalForm.direccion" label="Dirección" />
              </v-col>
              <v-col cols="12">
                <v-switch v-model="sucursalForm.activo" label="Activa" color="success" hide-details />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5">
          <v-spacer />
          <v-btn variant="text" @click="sucursalDialog = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="savingSucursal" @click="saveSucursal">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <ConfirmDialog
      v-model="confirmEmpresaOpen"
      :loading="deletingEmpresa"
      :message="`¿Eliminar la empresa «${deleteEmpresaTarget?.nombre}» y sus sucursales asociadas?`"
      @confirm="confirmDeleteEmpresa"
    />

    <ConfirmDialog
      v-model="confirmSucursalOpen"
      :loading="deletingSucursal"
      :message="`¿Eliminar la sucursal «${deleteSucursalTarget?.nombre}»?`"
      @confirm="confirmDeleteSucursal"
    />
  </div>
</template>

<style scoped>
.master-detail {
  overflow: hidden;
  min-height: 520px;
}

.master-panel {
  background: rgba(var(--v-theme-primary), 0.02);
  min-height: 520px;
}

.master-list__item {
  cursor: pointer;
  transition: background 0.15s ease;
}

.master-list__item.v-list-item--active {
  background: rgba(var(--v-theme-primary), 0.12) !important;
}

.detail-panel {
  min-height: 520px;
  position: relative;
}

.detail-progress {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2;
}

.detail-content {
  animation: detail-enter 0.25s ease;
}

.detail-chip-skeleton :deep(.v-skeleton-loader__chip) {
  margin: 0;
}

.detail-table-area {
  min-height: 280px;
}

.detail-skeleton {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

@keyframes detail-enter {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.detail-panel__header {
  background: rgb(var(--v-theme-surface));
}

.detail-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 12px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.detail-empty,
.empty-master {
  color: rgba(var(--v-theme-on-surface), 0.7);
}

@media (max-width: 960px) {
  .master-panel {
    border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    max-height: 320px;
    overflow-y: auto;
  }

  .detail-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .detail-toolbar .v-btn {
    width: 100%;
  }
}
</style>
