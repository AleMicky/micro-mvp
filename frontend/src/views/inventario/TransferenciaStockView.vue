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

interface DetalleRow {
  producto_id: number | null
  cantidad: number | null
}

const form = reactive({
  almacen_origen_id: null as number | null,
  almacen_destino_id: null as number | null,
  observaciones: '',
})

const detalles = ref<DetalleRow[]>([{ producto_id: null, cantidad: null }])

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

function addDetalle() {
  detalles.value.push({ producto_id: null, cantidad: null })
}

function removeDetalle(index: number) {
  if (detalles.value.length > 1) {
    detalles.value.splice(index, 1)
  }
}

async function submitForm() {
  if (!form.almacen_origen_id || !form.almacen_destino_id) {
    appStore.showError('Seleccione almacén origen y destino')
    return
  }
  if (form.almacen_origen_id === form.almacen_destino_id) {
    appStore.showError('El almacén origen y destino deben ser diferentes')
    return
  }
  const validDetalles = detalles.value.filter((d) => d.producto_id && d.cantidad)
  if (!validDetalles.length) {
    appStore.showError('Agregue al menos un detalle válido')
    return
  }
  saving.value = true
  try {
    await inventarioService.transferenciaStock({
      almacen_origen_id: form.almacen_origen_id,
      almacen_destino_id: form.almacen_destino_id,
      observaciones: form.observaciones || null,
      detalles: validDetalles.map((d) => ({
        producto_id: d.producto_id!,
        cantidad: d.cantidad!,
      })),
    })
    appStore.showSuccess('Transferencia registrada')
    form.observaciones = ''
    detalles.value = [{ producto_id: null, cantidad: null }]
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

onMounted(loadCatalogos)
</script>

<template>
  <v-card max-width="900">
    <v-card-title>Transferencia entre almacenes</v-card-title>
    <v-card-subtitle>Mover stock de un almacén a otro</v-card-subtitle>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <v-select
            v-model="form.almacen_origen_id"
            :items="almacenes"
            item-title="nombre"
            item-value="id"
            label="Almacén origen"
            :loading="loading"
          />
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="form.almacen_destino_id"
            :items="almacenes"
            item-title="nombre"
            item-value="id"
            label="Almacén destino"
            :loading="loading"
          />
        </v-col>
        <v-col cols="12">
          <v-textarea v-model="form.observaciones" label="Observaciones" rows="2" />
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <div class="d-flex align-center justify-space-between mb-3">
        <span class="text-subtitle-1 font-weight-medium">Productos a transferir</span>
        <v-btn size="small" prepend-icon="mdi-plus" variant="tonal" @click="addDetalle">Agregar línea</v-btn>
      </div>

      <v-row v-for="(detalle, index) in detalles" :key="index" align="center">
        <v-col cols="12" md="5">
          <v-select
            v-model="detalle.producto_id"
            :items="productos"
            item-title="nombre"
            item-value="id"
            label="Producto"
            :loading="loading"
          />
        </v-col>
        <v-col cols="12" md="5">
          <v-text-field
            v-model.number="detalle.cantidad"
            label="Cantidad"
            type="number"
            min="0"
            step="0.01"
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-btn
            icon="mdi-delete"
            variant="text"
            color="error"
            :disabled="detalles.length === 1"
            @click="removeDetalle(index)"
          />
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="primary" variant="flat" prepend-icon="mdi-truck-delivery" :loading="saving" @click="submitForm">
        Registrar transferencia
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
