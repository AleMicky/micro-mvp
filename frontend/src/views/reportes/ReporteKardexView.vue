<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { reportesService } from '@/services/reportes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'

const appStore = useAppStore()
const productoId = ref(1)
const loading = ref(false)
const items = ref<unknown[]>([])

async function loadData() {
  loading.value = true
  try {
    const { data } = await reportesService.getKardex(productoId.value)
    items.value = (data as { items?: unknown[] }).items ?? []
  } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
onMounted(loadData)
</script>

<template>
  <div>
    <PageHeader title="Reporte de kardex" subtitle="Movimientos por producto" icon="mdi-file-document-outline" />
    <v-card border elevation="0" class="pa-5">
      <v-row class="mb-4"><v-col cols="12" md="4"><v-text-field v-model.number="productoId" label="ID producto" type="number" /><v-btn color="primary" class="mt-2" :loading="loading" @click="loadData">Consultar</v-btn></v-col></v-row>
      <v-data-table :items="items" :loading="loading" item-value="id" />
    </v-card>
  </div>
</template>
