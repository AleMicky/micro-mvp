<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { finanzasService } from '@/services/finanzas.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Banco } from '@/types/finanzas.types'

const appStore = useAppStore()
const items = ref<Banco[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<Banco | null>(null)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const defaultForm = () => ({
  codigo: '',
  nombre: '',
  activo: true,
})

const form = reactive(defaultForm())

const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Estado', key: 'activo' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 120 },
]

async function loadData() {
  loading.value = true
  try {
    const { data } = await finanzasService.getBancos()
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

function openEdit(item: Banco) {
  editingId.value = item.id
  Object.assign(form, { codigo: item.codigo, nombre: item.nombre, activo: item.activo })
  dialog.value = true
}

function openDelete(item: Banco) {
  deleteTarget.value = item
  confirmOpen.value = true
}

async function saveItem() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid) return
  saving.value = true
  try {
    const payload = { codigo: form.codigo.trim(), nombre: form.nombre.trim(), activo: form.activo }
    if (editingId.value) {
      await finanzasService.updateBanco(editingId.value, payload)
      appStore.showSuccess('Registro actualizado')
    } else {
      await finanzasService.createBanco(payload)
      appStore.showSuccess('Registro creado')
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
    await finanzasService.deleteBanco(deleteTarget.value.id)
    appStore.showSuccess('Registro eliminado')
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
    title="Bancos"
    subtitle="Gestión de bancos"
  >
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nuevo</v-btn>
    </template>
    <template #item.activo="{ value }">
      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">{{ value ? 'Activo' : 'Inactivo' }}</v-chip>
    </template>
    <template #item.actions="{ item }">
      <v-btn icon="mdi-pencil-outline" size="small" variant="text" @click="openEdit(item)" />
      <v-btn icon="mdi-delete-outline" size="small" variant="text" color="error" @click="openDelete(item)" />
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="560" persistent>
    <v-card>
      <v-card-title class="pa-5">{{ editingId ? 'Editar' : 'Nuevo' }}</v-card-title>
      <v-card-text class="pa-5">
        <v-form ref="formRef">
          <v-text-field v-model="form.codigo" label="Código" :rules="[requiredRule]" />
          <v-text-field v-model="form.nombre" label="Nombre" :rules="[requiredRule]" />
          <v-switch v-model="form.activo" label="Activo" color="success" hide-details inset />
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-5">
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="saveItem">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <ConfirmDialog v-model="confirmOpen" :loading="deleting" message="¿Eliminar registro?" @confirm="confirmDelete" />
</template>
