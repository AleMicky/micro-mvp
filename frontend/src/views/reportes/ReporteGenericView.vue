<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { reportesService } from '@/services/reportes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'

const props = defineProps<{ tipo: string; title: string; loader: () => ReturnType<typeof reportesService.getStock> }>()

const appStore = useAppStore()
const loading = ref(false)
const reporte = ref<Record<string, unknown> | null>(null)
const items = ref<unknown[]>([])

async function loadData() {
  loading.value = true
  try {
    const { data } = await props.loader()
    reporte.value = data as Record<string, unknown>
    items.value = (data as { items?: unknown[] }).items ?? []
  } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}

onMounted(loadData)
</script>

<template>
  <div>
    <PageHeader :title="title" :subtitle="`Reporte ${tipo}`" icon="mdi-file-chart-outline" />
    <v-card border elevation="0" class="pa-5">
      <div class="text-body-2 text-medium-emphasis mb-4">Total registros: {{ reporte?.total ?? items.length }}</div>
      <v-data-table :items="items" :loading="loading" item-value="id" hover class="rounded-lg" />
    </v-card>
  </div>
</template>
