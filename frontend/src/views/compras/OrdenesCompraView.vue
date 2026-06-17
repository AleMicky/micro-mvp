<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { comprasService } from '@/services/compras.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { ESTADO_COMPRA_COLORS, type OrdenCompra } from '@/types/compras.types'

const appStore = useAppStore()
const items = ref<OrdenCompra[]>([])
const loading = ref(false)
const search = ref('')
const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Proveedor', key: 'proveedor_id' },
  { title: 'Total', key: 'total' },
  { title: 'Estado', key: 'estado' },
  { title: 'Fecha', key: 'fecha' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const },
]

async function loadData() {
  loading.value = true
  try { items.value = (await comprasService.getOrdenes()).data } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}

async function aprobar(item: OrdenCompra) {
  try { await comprasService.aprobarOrden(item.id); appStore.showSuccess('Orden aprobada'); await loadData() }
  catch (e) { appStore.showError(getErrorMessage(e)) }
}

onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Órdenes de compra" subtitle="Gestión de órdenes de compra">
    <template #item.estado="{ value }"><v-chip :color="ESTADO_COMPRA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip></template>
    <template #item.actions="{ item }">
      <v-btn v-if="['BORRADOR','PENDIENTE'].includes(item.estado)" size="small" color="primary" variant="tonal" @click="aprobar(item)">Aprobar</v-btn>
    </template>
  </BaseDataTable>
</template>
