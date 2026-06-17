<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { reportesService } from '@/services/reportes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'

const appStore = useAppStore()
const tipo = ref('stock')
const loading = ref(false)
const tipos = ['stock', 'productos', 'compras', 'ventas', 'finanzas']

async function exportar(formato: 'pdf' | 'excel') {
  loading.value = true
  try {
    const fn = formato === 'pdf' ? reportesService.exportarPdf : reportesService.exportarExcel
    const { data } = await fn(tipo.value)
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `reporte_${tipo.value}.${formato === 'pdf' ? 'txt' : 'csv'}`
    a.click()
    URL.revokeObjectURL(url)
    appStore.showSuccess(`Exportación ${formato.toUpperCase()} descargada`)
  } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
</script>

<template>
  <div>
    <PageHeader title="Exportar reportes" subtitle="Descarga en PDF o Excel (CSV)" icon="mdi-download" />
    <v-card border class="pa-5" max-width="480">
      <v-select v-model="tipo" :items="tipos" label="Tipo de reporte" />
      <div class="d-flex ga-3 mt-4">
        <v-btn color="primary" prepend-icon="mdi-file-pdf-box" :loading="loading" @click="exportar('pdf')">Exportar PDF</v-btn>
        <v-btn color="success" prepend-icon="mdi-file-excel" :loading="loading" @click="exportar('excel')">Exportar Excel</v-btn>
      </div>
    </v-card>
  </div>
</template>
