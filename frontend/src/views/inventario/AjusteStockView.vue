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
  cantidad_nueva: number | null
}

const form = reactive({
  almacen_id: null as number | null,
  motivo: '',
  observaciones: '',
})

const detalles = ref<DetalleRow[]>([{ producto_id: null, cantidad_nueva: null }])

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
  detalles.value.push({ producto_id: null, cantidad_nueva: null })
}

function removeDetalle(index: number) {
  if (detalles.value.length > 1) {
    detalles.value.splice(index, 1)
  }
}

async function submitForm() {
  if (!form.almacen_id) {
    appStore.showError('Seleccione un almacén')
    return
  }
  const validDetalles = detalles.value.filter((d) => d.producto_id && d.cantidad_nueva !== null)
  if (!validDetalles.length) {
    appStore.showError('Agregue al menos un detalle válido')
    return
  }
  saving.value = true
  try {
    await inventarioService.ajusteStock({
      almacen_id: form.almacen_id,
      motivo: form.motivo || null,
      observaciones: form.observaciones || null,
      detalles: validDetalles.map((d) => ({
        producto_id: d.producto_id!,
        cantidad_nueva: d.cantidad_nueva!,
      })),
    })
    appStore.showSuccess('Ajuste de stock registrado')
    form.motivo = ''
    form.observaciones = ''
    detalles.value = [{ producto_id: null, cantidad_nueva: null }]
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
    <v-card-title>Ajuste de stock</v-card-title>
    <v-card-subtitle>Corregir cantidades de inventario en un almacén</v-card-subtitle>
    <v-card-text>
      <v-row>
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
          <v-text-field v-model="form.motivo" label="Motivo" />
        </v-col>
        <v-col cols="12">
          <v-textarea v-model="form.observaciones" label="Observaciones" rows="2" />
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <div class="d-flex align-center justify-space-between mb-3">
        <span class="text-subtitle-1 font-weight-medium">Detalles del ajuste</span>
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
            v-model.number="detalle.cantidad_nueva"
            label="Cantidad nueva"
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
      <v-btn color="warning" variant="flat" prepend-icon="mdi-tune" :loading="saving" @click="submitForm">
        Registrar ajuste
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
