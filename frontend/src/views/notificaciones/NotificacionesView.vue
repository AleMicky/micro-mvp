<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { notificacionesService } from '@/services/notificaciones.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Notificacion } from '@/types/notificaciones.types'

const appStore = useAppStore()
const items = ref<Notificacion[]>([])
const loading = ref(false)
const search = ref('')
const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Cliente', key: 'cliente_id' },
  { title: 'Tipo', key: 'tipo' },
  { title: 'Contenido', key: 'contenido' },
  { title: 'Evento', key: 'evento_origen' },
  { title: 'Fecha', key: 'creado_en' },
]

async function loadData() {
  loading.value = true
  try {
    items.value = (await notificacionesService.getNotificaciones()).data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Notificaciones" subtitle="Eventos simulados del sistema">
    <template #actions><v-btn color="primary" prepend-icon="mdi-refresh" @click="loadData">Actualizar</v-btn></template>
  </BaseDataTable>
</template>
