<script setup lang="ts">
import { onMounted, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { clientesService } from '@/services/clientes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Cliente, HistorialCliente } from '@/types/clientes.types'

const appStore = useAppStore()
const clientes = ref<Cliente[]>([])
const historial = ref<HistorialCliente[]>([])
const clienteId = ref<number | null>(null)
const loading = ref(false)
const headers = [
  { title: 'Tipo', key: 'tipo' },
  { title: 'Descripción', key: 'descripcion' },
  { title: 'Monto', key: 'monto' },
  { title: 'Referencia', key: 'referencia' },
  { title: 'Fecha', key: 'creado_en' },
]

async function loadClientes() {
  try {
    clientes.value = (await clientesService.getClientes()).data
    if (clientes.value.length && !clienteId.value) clienteId.value = clientes.value[0].id
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  }
}

async function loadHistorial() {
  if (!clienteId.value) return
  loading.value = true
  try {
    historial.value = (await clientesService.getHistorial(clienteId.value)).data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
    historial.value = []
  } finally {
    loading.value = false
  }
}

async function onClienteChange() {
  await loadHistorial()
}

onMounted(async () => {
  await loadClientes()
  await loadHistorial()
})
</script>

<template>
  <v-card class="pa-5">
    <v-card-title>Historial de cliente</v-card-title>
    <v-card-subtitle>Compras, puntos y movimientos</v-card-subtitle>
    <v-select
      v-model="clienteId"
      :items="clientes"
      item-title="nombre"
      item-value="id"
      label="Cliente"
      class="mt-4"
      @update:model-value="onClienteChange"
    />
    <BaseDataTable :items="historial" :headers="headers" :loading="loading" title="" subtitle="" />
  </v-card>
</template>
