<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { finanzasService } from '@/services/finanzas.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { ESTADO_FINANZA_COLORS, type CuentaPorCobrar } from '@/types/finanzas.types'

const appStore = useAppStore()
const items = ref<CuentaPorCobrar[]>([])
const loading = ref(false)
const search = ref('')
const headers = [
  { title: 'Código', key: 'codigo' }, { title: 'Monto', key: 'monto' }, { title: 'Saldo', key: 'saldo' },
  { title: 'Estado', key: 'estado' }, { title: 'Descripción', key: 'descripcion' },
]

async function loadData() {
  loading.value = true
  try { items.value = (await finanzasService.getCuentasPorCobrar()).data } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Cuentas por cobrar" subtitle="Cartera de clientes">
    <template #item.estado="{ value }"><v-chip :color="ESTADO_FINANZA_COLORS[value] ?? 'default'" size="small" variant="tonal">{{ value }}</v-chip></template>
  </BaseDataTable>
</template>
