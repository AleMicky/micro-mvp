<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
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
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<Proveedor | null>(null)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const defaultForm = () => ({ codigo: '', nombre: '', rfc: '', email: '', telefono: '', direccion: '', activo: true })
const form = reactive(defaultForm())

const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Razón Social', key: 'nombre' },
  { title: 'NIT', key: 'rfc' },
  { title: 'Teléfono', key: 'telefono' },
  { title: 'Correo', key: 'email' },
  { title: 'Estado', key: 'activo' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 120 },
]

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

function openCreate() { editingId.value = null; Object.assign(form, defaultForm()); dialog.value = true }
function openEdit(item: Proveedor) {
  editingId.value = item.id
  Object.assign(form, { codigo: item.codigo, nombre: item.nombre, rfc: item.rfc ?? '', email: item.email ?? '', telefono: item.telefono ?? '', direccion: item.direccion ?? '', activo: item.activo })
  dialog.value = true
}
function openDelete(item: Proveedor) { deleteTarget.value = item; confirmOpen.value = true }

async function saveItem() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid) return
  saving.value = true
  try {
    const payload = { codigo: form.codigo.trim(), nombre: form.nombre.trim(), rfc: form.rfc || null, email: form.email || null, telefono: form.telefono || null, direccion: form.direccion || null, activo: form.activo }
    if (editingId.value) { await comprasService.updateProveedor(editingId.value, payload); appStore.showSuccess('Proveedor actualizado') }
    else { await comprasService.createProveedor(payload); appStore.showSuccess('Proveedor creado') }
    dialog.value = false
    await loadData()
  } catch (error) { appStore.showError(getErrorMessage(error)) } finally { saving.value = false }
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
  } catch (error) { appStore.showError(getErrorMessage(error)) } finally { deleting.value = false }
}

onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Proveedores" subtitle="Gestión de proveedores">
    <template #actions><v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nuevo</v-btn></template>
    <template #item.activo="{ value }"><v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">{{ value ? 'Activo' : 'Inactivo' }}</v-chip></template>
    <template #item.actions="{ item }">
      <v-btn icon="mdi-pencil-outline" size="small" variant="text" @click="openEdit(item)" />
      <v-btn icon="mdi-delete-outline" size="small" variant="text" color="error" @click="openDelete(item)" />
    </template>
  </BaseDataTable>
  <v-dialog v-model="dialog" max-width="640" persistent>
    <v-card>
      <v-card-title class="pa-5">{{ editingId ? 'Editar proveedor' : 'Nuevo proveedor' }}</v-card-title>
      <v-card-text class="pa-5"><v-form ref="formRef">
        <v-row>
          <v-col cols="12" md="6"><v-text-field v-model="form.codigo" label="Código" :rules="[requiredRule]" /></v-col>
          <v-col cols="12" md="6"><v-text-field v-model="form.nombre" label="Razón Social" :rules="[requiredRule]" /></v-col>
          <v-col cols="12" md="6"><v-text-field v-model="form.rfc" label="NIT" /></v-col>
          <v-col cols="12" md="6"><v-text-field v-model="form.email" label="Correo" /></v-col>
          <v-col cols="12" md="6"><v-text-field v-model="form.telefono" label="Teléfono" /></v-col>
          <v-col cols="12"><v-textarea v-model="form.direccion" label="Dirección" rows="2" /></v-col>
          <v-col cols="12"><v-switch v-model="form.activo" label="Activo" color="success" hide-details inset /></v-col>
        </v-row>
      </v-form></v-card-text>
      <v-card-actions class="pa-5"><v-spacer /><v-btn variant="text" @click="dialog = false">Cancelar</v-btn><v-btn color="primary" :loading="saving" @click="saveItem">Guardar</v-btn></v-card-actions>
    </v-card>
  </v-dialog>
  <ConfirmDialog v-model="confirmOpen" :loading="deleting" :message="`¿Desactivar proveedor «${deleteTarget?.nombre}»?`" @confirm="confirmDelete" />
</template>
