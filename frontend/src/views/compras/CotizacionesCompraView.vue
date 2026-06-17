<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { comprasService } from '@/services/compras.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { ESTADO_COMPRA_COLORS, type CotizacionCompra } from '@/types/compras.types'

const appStore = useAppStore()
const items = ref<CotizacionCompra[]>([])
const loading = ref(false)
const search = ref('')
const headers = [
  { title: 'Código', key: 'codigo' }, { title: 'Proveedor', key: 'proveedor_id' },
  { title: 'Total', key: 'total' }, { title: 'Estado', key: 'estado' }, { title: 'Fecha', key: 'fecha' },
]

async function loadData() {
  loading.value = true
  try { items.value = (await comprasService.getCotizaciones()).data } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Cotizaciones de compra" subtitle="Solicitudes y cotizaciones">
    <template #item.estado="{ value }"><v-chip :color="ESTADO_COMPRA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip></template>
  </BaseDataTable>
</template>
