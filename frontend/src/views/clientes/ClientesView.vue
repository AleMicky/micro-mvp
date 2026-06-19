<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { clientesService } from '@/services/clientes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Cliente } from '@/types/clientes.types'

const appStore = useAppStore()
const items = ref<Cliente[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const defaultForm = () => ({ codigo: '', nombre: '', email: '', telefono: '', documento: '', direccion: '', activo: true })
const form = reactive(defaultForm())
const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Documento', key: 'documento' },
  { title: 'Email', key: 'email' },
  { title: 'Estado', key: 'activo' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 80 },
]

async function loadData() {
  loading.value = true
  try {
    items.value = (await clientesService.getClientes()).data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, defaultForm())
  dialog.value = true
}

function openEdit(item: Cliente) {
  editingId.value = item.id
  Object.assign(form, {
    codigo: item.codigo,
    nombre: item.nombre,
    email: item.email ?? '',
    telefono: item.telefono ?? '',
    documento: item.documento ?? '',
    direccion: item.direccion ?? '',
    activo: item.activo,
  })
  dialog.value = true
}

async function saveItem() {
  if (!(await formRef.value?.validate())?.valid) return
  saving.value = true
  try {
    const payload = {
      codigo: form.codigo.trim(),
      nombre: form.nombre.trim(),
      email: form.email || null,
      telefono: form.telefono || null,
      documento: form.documento || null,
      direccion: form.direccion || null,
      activo: form.activo,
    }
    if (editingId.value) {
      await clientesService.updateCliente(editingId.value, payload)
      appStore.showSuccess('Cliente actualizado')
    } else {
      await clientesService.createCliente(payload)
      appStore.showSuccess('Cliente creado')
    }
    dialog.value = false
    await loadData()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Clientes" subtitle="Programa de fidelización">
    <template #actions><v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nuevo</v-btn></template>
    <template #item.activo="{ value }"><v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">{{ value ? 'Activo' : 'Inactivo' }}</v-chip></template>
    <template #item.actions="{ item }"><v-btn icon="mdi-pencil-outline" size="small" variant="text" @click="openEdit(item)" /></template>
  </BaseDataTable>
  <v-dialog v-model="dialog" max-width="640" persistent>
    <v-card>
      <v-card-title class="pa-5">{{ editingId ? 'Editar cliente' : 'Nuevo cliente' }}</v-card-title>
      <v-card-text class="pa-5">
        <v-form ref="formRef">
          <v-text-field v-model="form.codigo" label="Código" :rules="[requiredRule]" />
          <v-text-field v-model="form.nombre" label="Nombre" :rules="[requiredRule]" />
          <v-text-field v-model="form.documento" label="Documento" />
          <v-text-field v-model="form.email" label="Email" />
          <v-switch v-model="form.activo" label="Activo" color="success" />
        </v-form>
      </v-card-text>
      <v-card-actions class="pa-5"><v-spacer /><v-btn variant="text" @click="dialog = false">Cancelar</v-btn><v-btn color="primary" :loading="saving" @click="saveItem">Guardar</v-btn></v-card-actions>
    </v-card>
  </v-dialog>
</template>
