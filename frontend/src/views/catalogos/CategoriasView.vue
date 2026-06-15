<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { catalogosService } from '@/services/catalogos.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Categoria } from '@/types/catalogos.types'

const appStore = useAppStore()

const items = ref<Categoria[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<Categoria | null>(null)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const defaultForm = () => ({
  codigo: '',
  nombre: '',
  descripcion: '',
  activo: true,
})

const form = reactive(defaultForm())

const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Descripción', key: 'descripcion' },
  { title: 'Estado', key: 'activo' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 120 },
]

async function loadData() {
  loading.value = true
  try {
    const { data } = await catalogosService.getCategorias()
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

function openEdit(item: Categoria) {
  editingId.value = item.id
  Object.assign(form, {
    codigo: item.codigo,
    nombre: item.nombre,
    descripcion: item.descripcion ?? '',
    activo: item.activo,
  })
  dialog.value = true
}

function openDelete(item: Categoria) {
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
      descripcion: form.descripcion.trim() || null,
      activo: form.activo,
    }
    if (editingId.value) {
      await catalogosService.updateCategoria(editingId.value, payload)
      appStore.showSuccess('Categoría actualizada')
    } else {
      await catalogosService.createCategoria(payload)
      appStore.showSuccess('Categoría creada')
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
    await catalogosService.deleteCategoria(deleteTarget.value.id)
    appStore.showSuccess('Categoría eliminada')
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
    title="Categorías"
    subtitle="Gestión de categorías de productos"
    empty-subtitle="Crea la primera categoría con el botón Nuevo."
  >
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nuevo</v-btn>
    </template>

    <template #item.descripcion="{ value }">
      <span class="text-medium-emphasis">{{ value || '—' }}</span>
    </template>

    <template #item.activo="{ value }">
      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">
        {{ value ? 'Activo' : 'Inactivo' }}
      </v-chip>
    </template>

    <template #item.actions="{ item }">
      <v-tooltip text="Editar" location="top">
        <template #activator="{ props }">
          <v-btn v-bind="props" icon="mdi-pencil-outline" size="small" variant="text" @click="openEdit(item)" />
        </template>
      </v-tooltip>
      <v-tooltip text="Eliminar" location="top">
        <template #activator="{ props }">
          <v-btn v-bind="props" icon="mdi-delete-outline" size="small" variant="text" color="error" @click="openDelete(item)" />
        </template>
      </v-tooltip>
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="560" persistent>
    <v-card>
      <v-card-title class="pa-5 pb-2">
        <div class="text-h6">{{ editingId ? 'Editar categoría' : 'Nueva categoría' }}</div>
      </v-card-title>
      <v-card-text class="pa-5 pt-2">
        <v-form ref="formRef">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.codigo" label="Código" :rules="[requiredRule]" />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="form.nombre" label="Nombre" :rules="[requiredRule]" />
            </v-col>
            <v-col cols="12">
              <v-textarea v-model="form.descripcion" label="Descripción" rows="2" />
            </v-col>
            <v-col cols="12">
              <v-switch v-model="form.activo" label="Activo" color="success" hide-details inset />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-5 pt-0">
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="saveItem">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <ConfirmDialog
    v-model="confirmOpen"
    :loading="deleting"
    :message="`¿Eliminar la categoría «${deleteTarget?.nombre}»?`"
    @confirm="confirmDelete"
  />
</template>
