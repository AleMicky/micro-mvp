<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, getErrorMessage } from '@/services/api'
import { catalogosService } from '@/services/catalogos.service'
import { useAppStore } from '@/stores/app.store'
import type { Producto } from '@/types/catalogos.types'

const appStore = useAppStore()
const productos = ref<Producto[]>([])
const productoId = ref<number | null>(null)
const consolidado = ref<{ producto_id: number; cantidad_total: number; almacenes: number } | null>(null)
const loading = ref(false)

async function loadProductos() {
  try {
    productos.value = (await catalogosService.getProductos()).data
    if (productos.value.length) productoId.value = productos.value[0].id
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  }
}

async function consultar() {
  if (!productoId.value) return
  loading.value = true
  try {
    const { data } = await api.get(`/inventario/stock/consolidado/producto/${productoId.value}`)
    consolidado.value = data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadProductos()
  await consultar()
})
</script>

<template>
  <v-card class="pa-5">
    <v-card-title>Stock consolidado por producto</v-card-title>
    <v-select v-model="productoId" :items="productos" item-title="nombre" item-value="id" label="Producto" class="mt-4" />
    <v-btn color="primary" class="mt-2" :loading="loading" @click="consultar">Consultar</v-btn>
    <v-alert v-if="consolidado" type="success" variant="tonal" class="mt-4">
      Producto #{{ consolidado.producto_id }} — Total: <strong>{{ consolidado.cantidad_total }}</strong> unidades en
      <strong>{{ consolidado.almacenes }}</strong> almacén(es)
    </v-alert>
  </v-card>
</template>
