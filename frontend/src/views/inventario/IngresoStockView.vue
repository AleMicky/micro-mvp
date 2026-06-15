<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { positiveNumberRule, requiredRule } from '@/utils/validation'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen } from '@/types/inventario.types'

const appStore = useAppStore()

const productos = ref<Producto[]>([])
const almacenes = ref<Almacen[]>([])
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = reactive({
  producto_id: null as number | null,
  almacen_id: null as number | null,
  cantidad: null as number | null,
  stock_minimo: null as number | null,
  stock_maximo: null as number | null,
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
  const validation = await formRef.value?.validate()
  if (!validation?.valid) return

  saving.value = true
  try {
    await inventarioService.ingresoStock({
      producto_id: form.producto_id!,
      almacen_id: form.almacen_id!,
      cantidad: form.cantidad!,
      stock_minimo: form.stock_minimo,
      stock_maximo: form.stock_maximo,
      observaciones: form.observaciones.trim() || null,
    })
    appStore.showSuccess('Ingreso de stock registrado')
    form.cantidad = null
    form.stock_minimo = null
    form.stock_maximo = null
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
  <div>
    <PageHeader
      title="Ingreso de stock"
      subtitle="Registrar entrada de mercancía a un almacén"
      icon="mdi-arrow-down-bold-circle-outline"
    />

    <v-card class="form-card pa-6" max-width="760" border>
      <v-form ref="formRef" @submit.prevent="submitForm">
        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.producto_id"
              :items="productos"
              item-title="nombre"
              item-value="id"
              label="Producto"
              :loading="loading"
              :rules="[requiredRule]"
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
              :rules="[requiredRule]"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model.number="form.cantidad"
              label="Cantidad"
              type="number"
              min="0"
              step="0.01"
              :rules="[requiredRule, positiveNumberRule]"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field v-model.number="form.stock_minimo" label="Stock mínimo" type="number" min="0" />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field v-model.number="form.stock_maximo" label="Stock máximo" type="number" min="0" />
          </v-col>
          <v-col cols="12">
            <v-textarea v-model="form.observaciones" label="Observaciones" rows="2" />
          </v-col>
        </v-row>
        <div class="d-flex justify-end mt-2">
          <v-btn color="success" variant="flat" prepend-icon="mdi-check" :loading="saving" type="submit">
            Registrar ingreso
          </v-btn>
        </div>
      </v-form>
    </v-card>
  </div>
</template>
