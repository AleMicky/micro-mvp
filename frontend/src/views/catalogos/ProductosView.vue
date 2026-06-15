<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { catalogosService } from '@/services/catalogos.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Categoria, Marca, Producto, UnidadMedida } from '@/types/catalogos.types'

const appStore = useAppStore()

const items = ref<Producto[]>([])
const categorias = ref<Categoria[]>([])
const marcas = ref<Marca[]>([])
const unidades = ref<UnidadMedida[]>([])
const loading = ref(false)
const search = ref('')
const dialog = ref(false)
const confirmOpen = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const deleteTarget = ref<Producto | null>(null)

const defaultForm = () => ({
  codigo: '',
  nombre: '',
  descripcion: '',
  categoria_id: null as number | null,
  marca_id: null as number | null,
  unidad_medida_id: null as number | null,
  activo: true,
})

const form = reactive(defaultForm())

const categoriaMap = computed(() => Object.fromEntries(categorias.value.map((c) => [c.id, c.nombre])))
const marcaMap = computed(() => Object.fromEntries(marcas.value.map((m) => [m.id, m.nombre])))
const unidadMap = computed(() => Object.fromEntries(unidades.value.map((u) => [u.id, u.abreviatura])))

const headers = [
  { title: 'Código', key: 'codigo' },
  { title: 'Nombre', key: 'nombre' },
  { title: 'Categoría', key: 'categoria_id' },
  { title: 'Marca', key: 'marca_id' },
  { title: 'Unidad', key: 'unidad_medida_id' },
  { title: 'Estado', key: 'activo' },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const },
]

async function loadData() {
  loading.value = true
  try {
    const [productosRes, categoriasRes, marcasRes, unidadesRes] = await Promise.all([
      catalogosService.getProductos(),
      catalogosService.getCategorias(),
      catalogosService.getMarcas(),
      catalogosService.getUnidadesMedida(),
    ])
    items.value = productosRes.data
    categorias.value = categoriasRes.data
    marcas.value = marcasRes.data
    unidades.value = unidadesRes.data
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, defaultForm())
  dialog.value = true
}

function openEdit(item: Producto) {
  editingId.value = item.id
  Object.assign(form, {
    codigo: item.codigo,
    nombre: item.nombre,
    descripcion: item.descripcion ?? '',
    categoria_id: item.categoria_id,
    marca_id: item.marca_id,
    unidad_medida_id: item.unidad_medida_id,
    activo: item.activo,
  })
  dialog.value = true
}

function openDelete(item: Producto) {
  deleteTarget.value = item
  confirmOpen.value = true
}

async function saveItem() {
  if (!form.categoria_id || !form.unidad_medida_id) {
    appStore.showError('Seleccione categoría y unidad de medida')
    return
  }
  saving.value = true
  try {
    const payload = {
      codigo: form.codigo,
      nombre: form.nombre,
      descripcion: form.descripcion || null,
      categoria_id: form.categoria_id,
      marca_id: form.marca_id,
      unidad_medida_id: form.unidad_medida_id,
      activo: form.activo,
    }
    if (editingId.value) {
      await catalogosService.updateProducto(editingId.value, payload)
      appStore.showSuccess('Producto actualizado')
    } else {
      await catalogosService.createProducto(payload)
      appStore.showSuccess('Producto creado')
    }
    dialog.value = false
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await catalogosService.deleteProducto(deleteTarget.value.id)
    appStore.showSuccess('Producto eliminado')
    confirmOpen.value = false
    deleteTarget.value = null
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    deleting.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <BaseDataTable
    v-model:search="search"
    :items="items"
    :headers="headers"
    :loading="loading"
    title="Productos"
    subtitle="Gestión de productos del catálogo"
  >
    <template #actions>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreate">Nuevo</v-btn>
    </template>

    <template #item.categoria_id="{ value }">
      {{ categoriaMap[value] ?? value }}
    </template>

    <template #item.marca_id="{ value }">
      {{ value ? (marcaMap[value] ?? value) : '—' }}
    </template>

    <template #item.unidad_medida_id="{ value }">
      {{ unidadMap[value] ?? value }}
    </template>

    <template #item.activo="{ value }">
      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">
        {{ value ? 'Activo' : 'Inactivo' }}
      </v-chip>
    </template>

    <template #item.actions="{ item }">
      <v-btn icon="mdi-pencil" size="small" variant="text" @click="openEdit(item)" />
      <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="openDelete(item)" />
    </template>
  </BaseDataTable>

  <v-dialog v-model="dialog" max-width="640" persistent scrollable>
    <v-card>
      <v-card-title>{{ editingId ? 'Editar producto' : 'Nuevo producto' }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.codigo" label="Código" />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.nombre" label="Nombre" />
          </v-col>
          <v-col cols="12">
            <v-textarea v-model="form.descripcion" label="Descripción" rows="2" />
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.categoria_id"
              :items="categorias"
              item-title="nombre"
              item-value="id"
              label="Categoría"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.marca_id"
              :items="marcas"
              item-title="nombre"
              item-value="id"
              label="Marca (opcional)"
              clearable
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.unidad_medida_id"
              :items="unidades"
              item-title="nombre"
              item-value="id"
              label="Unidad de medida"
            />
          </v-col>
          <v-col cols="12" md="6" class="d-flex align-center">
            <v-switch v-model="form.activo" label="Activo" color="success" hide-details />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="saveItem">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <ConfirmDialog
    v-model="confirmOpen"
    :loading="deleting"
    :message="`¿Eliminar el producto «${deleteTarget?.nombre}»?`"
    @confirm="confirmDelete"
  />
</template>
