<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { companyService } from '@/services/company.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Almacen } from '@/types/inventario.types'
import type { Compania, Sucursal } from '@/types/company.types'

const appStore = useAppStore()

const items = ref<Almacen[]>([])
const sucursales = ref<Sucursal[]>([])
const companias = ref<Compania[]>([])
const loading = ref(false)
const loadingSucursales = ref(false)
const search = ref('')
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<Almacen | null>(null)

const defaultForm = () => ({
  codigo: '',
  nombre: '',
  direccion: '',
  sucursal_id: null as number | null,
  activo: true,
})

const form = reactive(defaultForm())

const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Sucursal', key: 'sucursal_nombre' },
  { title: 'Compañía', key: 'compania_nombre' },
  { title: 'Estado', key: 'activo' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const },
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
      label: `${companiaPorId.get(s.compania_id) ?? '—'} - ${s.nombre}`,
    }))
    .sort((a, b) => {
      const cmp = a.compania_nombre.localeCompare(b.compania_nombre)
      return cmp !== 0 ? cmp : a.nombre.localeCompare(b.nombre)
    })
})

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
  saving.value = true
  try {
    const payload = {
      codigo: form.codigo,
      nombre: form.nombre,
      direccion: form.direccion || null,
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
  <BaseDataTable
    v-model:search="search"
    :items="items"
    :headers="headers"
    :loading="loading"
    title="Almacenes"
    subtitle="Gestión de almacenes"
  >
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nuevo</v-btn>
    </template>

    <template #item.sucursal_nombre="{ value }">
      {{ value || '—' }}
    </template>

    <template #item.compania_nombre="{ value }">
      {{ value || '—' }}
    </template>

    <template #item.activo="{ value }">
      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">
        {{ value ? 'Activo' : 'Inactivo' }}
      </v-chip>
    </template>

    <template #item.actions="{ item }">
      <v-btn icon="mdi-pencil" size="small" variant="text" @click="openEdit(item)" />
      <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="openDelete(item)" />
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="560" persistent>
    <v-card>
      <v-card-title>{{ editingId ? 'Editar almacén' : 'Nuevo almacén' }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.codigo" label="Código" />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.nombre" label="Nombre" />
          </v-col>
          <v-col cols="12">
            <v-select
              v-model="form.sucursal_id"
              :items="sucursalOptions"
              item-title="label"
              item-value="id"
              label="Sucursal"
              clearable
              :loading="loadingSucursales"
              hint="Opcional. Asocia el almacén a una sucursal."
              persistent-hint
            />
          </v-col>
          <v-col cols="12">
            <v-textarea v-model="form.direccion" label="Dirección" rows="2" />
          </v-col>
          <v-col cols="12">
            <v-switch v-model="form.activo" label="Activo" color="success" hide-details />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="saveItem">Guardar</v-btn>
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
