<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'

const appStore = useAppStore()
const reporte = ref<{ fecha: string; total_ventas: number; monto_total: number } | null>(null)
const loading = ref(false)
const fecha = ref(new Date().toISOString().slice(0, 10))

async function cargar() {
  loading.value = true
  try {
    const { data } = await api.get('/ventas/ventas/reporte/dia', { params: { fecha: fecha.value } })
    reporte.value = data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <v-card class="pa-5">
    <v-card-title>Reporte de ventas del día</v-card-title>
    <v-text-field v-model="fecha" type="date" label="Fecha" class="mt-4" />
    <v-btn color="primary" :loading="loading" @click="cargar">Consultar</v-btn>
    <v-row v-if="reporte" class="mt-4">
      <v-col cols="12" md="4"><v-card variant="tonal" color="primary" class="pa-4 text-center"><div class="text-h4">{{ reporte.total_ventas }}</div><div>Ventas</div></v-card></v-col>
      <v-col cols="12" md="4"><v-card variant="tonal" color="success" class="pa-4 text-center"><div class="text-h4">Bs {{ reporte.monto_total.toFixed(2) }}</div><div>Monto total</div></v-card></v-col>
      <v-col cols="12" md="4"><v-card variant="tonal" class="pa-4 text-center"><div class="text-h6">{{ reporte.fecha }}</div><div>Fecha</div></v-card></v-col>
    </v-row>
  </v-card>
</template>
