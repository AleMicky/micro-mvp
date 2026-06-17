<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { ventasService } from '@/services/ventas.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { ESTADO_VENTA_COLORS, type CotizacionVenta } from '@/types/ventas.types'

const appStore = useAppStore()
const items = ref<CotizacionVenta[]>([])
const loading = ref(false)
const search = ref('')
const headers = [
  { title: 'Código', key: 'codigo' }, { title: 'Cliente', key: 'cliente_id' },
  { title: 'Total', key: 'total' }, { title: 'Estado', key: 'estado' }, { title: 'Fecha', key: 'fecha' },
]

async function loadData() {
  loading.value = true
  try { items.value = (await ventasService.getCotizaciones()).data } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Cotizaciones de venta" subtitle="Propuestas comerciales">
    <template #item.estado="{ value }"><v-chip :color="ESTADO_VENTA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip></template>
  </BaseDataTable>
</template>
