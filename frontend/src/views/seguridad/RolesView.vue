<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { authService } from '@/services/auth.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Rol } from '@/types/auth.types'

const appStore = useAppStore()

const items = ref<Rol[]>([])
const loading = ref(false)
const search = ref('')

const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Descripción', key: 'descripcion' },
  { title: 'Permisos', key: 'permisos' },
  { title: 'Estado', key: 'activo' },
]

async function loadData() {
  loading.value = true
  try {
    const { data } = await authService.getRoles()
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
    title="Roles"
    subtitle="Consulta de roles y permisos asignados"
  >
    <template #item.descripcion="{ value }">
      {{ value || '—' }}
    </template>

    <template #item.permisos="{ value }">
      <v-chip
        v-for="permiso in value"
        :key="permiso.id"
        size="x-small"
        class="mr-1 mb-1"
        variant="outlined"
      >
        {{ permiso.codigo }}
      </v-chip>
    </template>

    <template #item.activo="{ value }">
      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">
        {{ value ? 'Activo' : 'Inactivo' }}
      </v-chip>
    </template>
  </BaseDataTable>
</template>
