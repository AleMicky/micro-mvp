<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { ventasService } from '@/services/ventas.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { ESTADO_VENTA_COLORS, type Venta } from '@/types/ventas.types'

const appStore = useAppStore()
const items = ref<Venta[]>([])
const loading = ref(false)
const search = ref('')
const headers = [
  { title: 'Código', key: 'codigo' }, { title: 'Cliente', key: 'cliente_id' },
  { title: 'Total', key: 'total' }, { title: 'Estado', key: 'estado' }, { title: 'Fecha', key: 'fecha' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const },
]

async function loadData() {
  loading.value = true
  try { items.value = (await ventasService.getVentas()).data } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
async function confirmar(item: Venta) {
  try { await ventasService.confirmarVenta(item.id); appStore.showSuccess('Venta confirmada'); await loadData() }
  catch (e) { appStore.showError(getErrorMessage(e)) }
}
onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Ventas" subtitle="Registro de ventas">
    <template #item.estado="{ value }"><v-chip :color="ESTADO_VENTA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip></template>
    <template #item.actions="{ item }">
      <v-btn v-if="['BORRADOR','PENDIENTE'].includes(item.estado)" size="small" color="primary" variant="tonal" @click="confirmar(item)">Confirmar</v-btn>
    </template>
  </BaseDataTable>
</template>
