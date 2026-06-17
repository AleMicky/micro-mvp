<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { reportesService } from '@/services/reportes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'

const appStore = useAppStore()
const loading = ref(false)
const cxc = ref<unknown[]>([])
const cxp = ref<unknown[]>([])

async function loadData() {
  loading.value = true
  try {
    const { data } = await reportesService.getFinanzas()
    cxc.value = (data as { cuentas_por_cobrar?: unknown[] }).cuentas_por_cobrar ?? []
    cxp.value = (data as { cuentas_por_pagar?: unknown[] }).cuentas_por_pagar ?? []
  } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
onMounted(loadData)
</script>

<template>
  <div>
    <PageHeader title="Reporte financiero" subtitle="Resumen CXC y CXP" icon="mdi-cash-multiple" />
    <v-row>
      <v-col cols="12" md="6"><v-card border class="pa-5"><div class="text-h6 mb-3">Cuentas por cobrar</div><v-data-table :items="cxc" :loading="loading" /></v-card></v-col>
      <v-col cols="12" md="6"><v-card border class="pa-5"><div class="text-h6 mb-3">Cuentas por pagar</div><v-data-table :items="cxp" :loading="loading" /></v-card></v-col>
    </v-row>
  </div>
</template>
