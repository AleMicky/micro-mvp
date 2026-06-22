<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { chatbotService } from '@/services/chatbot.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Etiqueta } from '@/types/chatbot.types'

const appStore = useAppStore()

const items = ref<Etiqueta[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<Etiqueta | null>(null)

const defaultForm = () => ({
  nombre: '',
  color: '#64748b',
})

const form = reactive(defaultForm())

const headers = [
  { title: 'Etiqueta', key: 'nombre' },
  { title: 'Color', key: 'color' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const },
]

async function loadData() {
  loading.value = true
  try {
    const { data } = await chatbotService.getEtiquetas()
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

function openEdit(item: Etiqueta) {
  editingId.value = item.id
  Object.assign(form, { nombre: item.nombre, color: item.color })
  dialog.value = true
}

function openDelete(item: Etiqueta) {
  deleteTarget.value = item
  confirmOpen.value = true
}

async function saveItem() {
  saving.value = true
  try {
    const payload = { nombre: form.nombre, color: form.color }
    if (editingId.value) {
      await chatbotService.updateEtiqueta(editingId.value, payload)
      appStore.showSuccess('Etiqueta actualizada')
    } else {
      await chatbotService.createEtiqueta(payload)
      appStore.showSuccess('Etiqueta creada')
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
    await chatbotService.deleteEtiqueta(deleteTarget.value.id)
    appStore.showSuccess('Etiqueta eliminada')
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
    title="Etiquetas"
    subtitle="Clasificación de conversaciones del chatbot"
  >
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nueva</v-btn>
    </template>

    <template #item.nombre="{ item }">
      <v-chip :style="{ backgroundColor: item.color, color: '#fff' }" size="small">{{ item.nombre }}</v-chip>
    </template>

    <template #item.color="{ value }">
      <span class="etiquetas-color-swatch" :style="{ backgroundColor: value }" />
      <span class="ml-2">{{ value }}</span>
    </template>

    <template #item.actions="{ item }">
      <v-btn icon="mdi-pencil" size="small" variant="text" @click="openEdit(item)" />
      <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="openDelete(item)" />
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="480" persistent>
    <v-card>
      <v-card-title>{{ editingId ? 'Editar etiqueta' : 'Nueva etiqueta' }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-text-field v-model="form.nombre" label="Nombre" maxlength="50" />
          </v-col>
          <v-col cols="12" class="d-flex align-center ga-3">
            <input v-model="form.color" type="color" class="etiquetas-color-input" />
            <v-text-field v-model="form.color" label="Color (hex)" maxlength="7" hide-details density="compact" />
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
    :message="`¿Eliminar la etiqueta «${deleteTarget?.nombre}»? Se quitará de todas las conversaciones donde esté asignada.`"
    @confirm="confirmDelete"
  />
</template>

<style scoped>
.etiquetas-color-swatch {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 4px;
  vertical-align: middle;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.etiquetas-color-input {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 6px;
  padding: 0;
  cursor: pointer;
}
</style>
