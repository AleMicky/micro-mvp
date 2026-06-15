<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { catalogosService } from '@/services/catalogos.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { UnidadMedida } from '@/types/catalogos.types'

const appStore = useAppStore()

const items = ref<UnidadMedida[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<UnidadMedida | null>(null)

const defaultForm = () => ({
  codigo: '',
  nombre: '',
  abreviatura: '',
  activo: true,
})

const form = reactive(defaultForm())

const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Abreviatura', key: 'abreviatura' },
  { title: 'Estado', key: 'activo' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const },
]

async function loadData() {
  loading.value = true
  try {
    const { data } = await catalogosService.getUnidadesMedida()
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

function openEdit(item: UnidadMedida) {
  editingId.value = item.id
  Object.assign(form, {
    codigo: item.codigo,
    nombre: item.nombre,
    abreviatura: item.abreviatura,
    activo: item.activo,
  })
  dialog.value = true
}

function openDelete(item: UnidadMedida) {
  deleteTarget.value = item
  confirmOpen.value = true
}

async function saveItem() {
  saving.value = true
  try {
    const payload = {
      codigo: form.codigo,
      nombre: form.nombre,
      abreviatura: form.abreviatura,
      activo: form.activo,
    }
    if (editingId.value) {
      await catalogosService.updateUnidadMedida(editingId.value, payload)
      appStore.showSuccess('Unidad de medida actualizada')
    } else {
      await catalogosService.createUnidadMedida(payload)
      appStore.showSuccess('Unidad de medida creada')
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
    await catalogosService.deleteUnidadMedida(deleteTarget.value.id)
    appStore.showSuccess('Unidad de medida eliminada')
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
  <BaseDataTable
    v-model:search="search"
    :items="items"
    :headers="headers"
    :loading="loading"
    title="Unidades de medida"
    subtitle="Gestión de unidades de medida"
  >
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nuevo</v-btn>
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
      <v-card-title>{{ editingId ? 'Editar unidad' : 'Nueva unidad de medida' }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field v-model="form.codigo" label="Código" />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field v-model="form.nombre" label="Nombre" />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field v-model="form.abreviatura" label="Abreviatura" />
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
    :message="`¿Eliminar la unidad «${deleteTarget?.nombre}»?`"
    @confirm="confirmDelete"
  />
</template>
