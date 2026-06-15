<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen } from '@/types/inventario.types'

const appStore = useAppStore()

const productos = ref<Producto[]>([])
const almacenes = ref<Almacen[]>([])
const loading = ref(false)
const saving = ref(false)

const form = reactive({
  producto_id: null as number | null,
  almacen_id: null as number | null,
  cantidad: null as number | null,
  observaciones: '',
})

async function loadCatalogos() {
  loading.value = true
  try {
    const [productosRes, almacenesRes] = await Promise.all([
      catalogosService.getProductos(),
      inventarioService.getAlmacenes(),
    ])
    productos.value = productosRes.data
    almacenes.value = almacenesRes.data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  if (!form.producto_id || !form.almacen_id || !form.cantidad) {
    appStore.showError('Complete los campos obligatorios')
    return
  }
  saving.value = true
  try {
    await inventarioService.salidaStock({
      producto_id: form.producto_id,
      almacen_id: form.almacen_id,
      cantidad: form.cantidad,
      observaciones: form.observaciones || null,
    })
    appStore.showSuccess('Salida de stock registrada')
    form.cantidad = null
    form.observaciones = ''
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

onMounted(loadCatalogos)
</script>

<template>
  <v-card max-width="720">
    <v-card-title>Salida de stock</v-card-title>
    <v-card-subtitle>Registrar salida de mercancía de un almacén</v-card-subtitle>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <v-select
            v-model="form.producto_id"
            :items="productos"
            item-title="nombre"
            item-value="id"
            label="Producto"
            :loading="loading"
          />
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="form.almacen_id"
            :items="almacenes"
            item-title="nombre"
            item-value="id"
            label="Almacén"
            :loading="loading"
          />
        </v-col>
        <v-col cols="12" md="6">
          <v-text-field v-model.number="form.cantidad" label="Cantidad" type="number" min="0" step="0.01" />
        </v-col>
        <v-col cols="12">
          <v-textarea v-model="form.observaciones" label="Observaciones" rows="2" />
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="error" variant="flat" prepend-icon="mdi-arrow-up-bold" :loading="saving" @click="submitForm">
        Registrar salida
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
