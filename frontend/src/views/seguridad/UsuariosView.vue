<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { authService } from '@/services/auth.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Usuario } from '@/types/auth.types'

const appStore = useAppStore()

const items = ref<Usuario[]>([])
const loading = ref(false)
const search = ref('')

const headers = [
  { title: 'Usuario', key: 'nombre_usuario' },
  { title: 'Nombre completo', key: 'nombre_completo' },
  { title: 'Correo', key: 'correo' },
  { title: 'Roles', key: 'roles' },
  { title: 'Estado', key: 'activo' },
  { title: 'Último login', key: 'ultimo_login_en' },
]

async function loadData() {
  loading.value = true
  try {
    const { data } = await authService.getUsuarios()
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
    title="Usuarios"
    subtitle="Consulta de usuarios del sistema"
  >
    <template #item.roles="{ value }">
      <v-chip
        v-for="rol in value"
        :key="rol.id"
        size="small"
        class="mr-1 mb-1"
        variant="tonal"
        color="primary"
      >
        {{ rol.nombre }}
      </v-chip>
    </template>

    <template #item.activo="{ value }">
      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">
        {{ value ? 'Activo' : 'Inactivo' }}
      </v-chip>
    </template>

    <template #item.ultimo_login_en="{ value }">
      {{ value ? new Date(value).toLocaleString('es-MX') : '—' }}
    </template>
  </BaseDataTable>
</template>
