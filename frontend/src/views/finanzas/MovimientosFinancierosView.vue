<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { finanzasService } from '@/services/finanzas.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'

const appStore = useAppStore()
const movCaja = ref<unknown[]>([])
const movBanco = ref<unknown[]>([])
const loading = ref(false)
const tab = ref('caja')

async function loadData() {
  loading.value = true
  try {
    const [caja, banco] = await Promise.all([finanzasService.getMovimientosCaja(), finanzasService.getMovimientosBancarios()])
    movCaja.value = caja.data
    movBanco.value = banco.data
  } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
onMounted(loadData)
</script>

<template>
  <v-card border elevation="0">
    <v-card-title class="pa-5"><div class="text-h6">Movimientos financieros</div></v-card-title>
    <v-tabs v-model="tab" class="px-5"><v-tab value="caja">Caja</v-tab><v-tab value="banco">Bancarios</v-tab></v-tabs>
    <v-card-text class="pa-5">
      <v-data-table v-if="tab === 'caja'" :items="movCaja" :loading="loading" :headers="[{ title: 'Caja', key: 'caja_id' }, { title: 'Tipo', key: 'tipo' }, { title: 'Monto', key: 'monto' }, { title: 'Referencia', key: 'referencia' }]" />
      <v-data-table v-else :items="movBanco" :loading="loading" :headers="[{ title: 'Cuenta', key: 'cuenta_bancaria_id' }, { title: 'Tipo', key: 'tipo' }, { title: 'Monto', key: 'monto' }, { title: 'Referencia', key: 'referencia' }]" />
    </v-card-text>
  </v-card>
</template>
