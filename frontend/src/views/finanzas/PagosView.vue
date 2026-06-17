<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import { finanzasService } from '@/services/finanzas.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Pago } from '@/types/finanzas.types'

const appStore = useAppStore()
const items = ref<Pago[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const saving = ref(false)
const form = reactive({ cuenta_pagar_id: 1, monto: '', metodo: 'TRANSFERENCIA', fecha: '' })
const headers = [
  { title: 'ID', key: 'id' }, { title: 'Cuenta CXP', key: 'cuenta_pagar_id' },
  { title: 'Monto', key: 'monto' }, { title: 'Método', key: 'metodo' }, { title: 'Fecha', key: 'fecha' },
]

async function loadData() {
  loading.value = true
  try { items.value = (await finanzasService.getPagos()).data } catch (e) { appStore.showError(getErrorMessage(e)) } finally { loading.value = false }
}
async function saveItem() {
  saving.value = true
  try {
    await finanzasService.registrarPago({ cuenta_pagar_id: form.cuenta_pagar_id, monto: form.monto, metodo: form.metodo, fecha: form.fecha || null })
    appStore.showSuccess('Pago registrado'); dialog.value = false; await loadData()
  } catch (e) { appStore.showError(getErrorMessage(e)) } finally { saving.value = false }
}
onMounted(loadData)
</script>

<template>
  <BaseDataTable v-model:search="search" :items="items" :headers="headers" :loading="loading" title="Pagos" subtitle="Registro de pagos">
    <template #actions><v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">Nuevo pago</v-btn></template>
  </BaseDataTable>
  <v-dialog v-model="dialog" max-width="480" persistent>
    <v-card><v-card-title class="pa-5">Registrar pago</v-card-title>
      <v-card-text class="pa-5">
        <v-text-field v-model.number="form.cuenta_pagar_id" label="ID cuenta por pagar" type="number" :rules="[requiredRule]" />
        <v-text-field v-model="form.monto" label="Monto" :rules="[requiredRule]" />
        <v-text-field v-model="form.metodo" label="Método" />
        <v-text-field v-model="form.fecha" label="Fecha" />
      </v-card-text>
      <v-card-actions class="pa-5"><v-spacer /><v-btn variant="text" @click="dialog = false">Cancelar</v-btn><v-btn color="primary" :loading="saving" @click="saveItem">Guardar</v-btn></v-card-actions>
    </v-card>
  </v-dialog>
</template>
