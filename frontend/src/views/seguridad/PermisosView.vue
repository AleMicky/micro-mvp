<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { authService } from '@/services/auth.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Permiso } from '@/types/auth.types'

const appStore = useAppStore()

const items = ref<Permiso[]>([])
const loading = ref(false)
const search = ref('')

const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Módulo', key: 'modulo' },
  { title: 'Descripción', key: 'descripcion' },
  { title: 'Estado', key: 'activo' },
]

async function loadData() {
  loading.value = true
  try {
    const { data } = await authService.getPermisos()
    items.value = data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
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
    title="Permisos"
    subtitle="Consulta de permisos del sistema"
  >
    <template #item.modulo="{ value }">
      <v-chip size="small" variant="tonal" color="info">{{ value }}</v-chip>
    </template>

    <template #item.descripcion="{ value }">
      {{ value || '—' }}
    </template>

    <template #item.activo="{ value }">
      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">
        {{ value ? 'Activo' : 'Inactivo' }}
      </v-chip>
    </template>
  </BaseDataTable>
</template>
