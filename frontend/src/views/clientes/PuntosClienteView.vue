<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { clientesService } from '@/services/clientes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Cliente } from '@/types/clientes.types'

const appStore = useAppStore()
const clientes = ref<Cliente[]>([])
const loading = ref(false)
const puntos = ref(0)
const clienteId = ref<number | null>(null)
const cantidadPuntos = ref(10)
const asignando = ref(false)

async function loadClientes() {
  loading.value = true
  try {
    clientes.value = (await clientesService.getClientes()).data
    if (clientes.value.length) {
      clienteId.value = clientes.value[0].id
      await loadPuntos()
    }
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

async function loadPuntos() {
  if (!clienteId.value) return
  try {
    const { data } = await clientesService.getCliente(clienteId.value)
    puntos.value = data.total_puntos ?? 0
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  }
}

async function asignar() {
  if (!clienteId.value || cantidadPuntos.value <= 0) return
  asignando.value = true
  try {
    await clientesService.asignarPuntos(clienteId.value, cantidadPuntos.value, 'Asignación manual')
    appStore.showSuccess('Puntos asignados')
    await loadPuntos()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    asignando.value = false
  }
}

onMounted(loadClientes)
</script>

<template>
  <v-card class="pa-5">
    <v-card-title>Puntos de fidelización</v-card-title>
    <v-select v-model="clienteId" :items="clientes" item-title="nombre" item-value="id" label="Cliente" class="mt-4" @update:model-value="loadPuntos" />
    <v-alert type="info" variant="tonal" class="my-4">Total de puntos: <strong>{{ puntos }}</strong></v-alert>
    <v-text-field v-model.number="cantidadPuntos" type="number" label="Puntos a asignar" min="1" />
    <v-btn color="primary" :loading="asignando" @click="asignar">Asignar puntos</v-btn>
  </v-card>
</template>
