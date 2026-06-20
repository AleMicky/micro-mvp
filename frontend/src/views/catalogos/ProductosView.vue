<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import PageHeader from '@/components/PageHeader.vue'
import { catalogosService } from '@/services/catalogos.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Categoria, Marca, PrecioProducto, Producto, UnidadMedida } from '@/types/catalogos.types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const appStore = useAppStore()

const categorias = ref<Categoria[]>([])
const allProductos = ref<Producto[]>([])
const marcas = ref<Marca[]>([])
const unidades = ref<UnidadMedida[]>([])
const selectedCategoriaId = ref<number | null>(null)
const loadingCategorias = ref(false)
const loadingProductos = ref(false)
const isDetailTransition = ref(false)
const searchCategorias = ref('')
const searchProductos = ref('')

const categoriaDialog = ref(false)
const productoDialog = ref(false)
const confirmCategoriaOpen = ref(false)
const confirmProductoOpen = ref(false)
const precioDialog = ref(false)
const historialDialog = ref(false)
const savingPrecio = ref(false)
const loadingHistorial = ref(false)
const uploadingImagen = ref(false)
const precioTarget = ref<Producto | null>(null)
const historialTarget = ref<Producto | null>(null)
const historialPrecios = ref<PrecioProducto[]>([])
const nuevoPrecio = ref<number | null>(null)
const imagenInputRef = ref<HTMLInputElement | null>(null)
const imagenTarget = ref<Producto | null>(null)
const formImagenInputRef = ref<HTMLInputElement | null>(null)
const formImagenFile = ref<File | null>(null)
const formImagenPreview = ref<string | null>(null)
const savingCategoria = ref(false)
const savingProducto = ref(false)
const deletingCategoria = ref(false)
const deletingProducto = ref(false)
const editingCategoriaId = ref<number | null>(null)
const editingProductoId = ref<number | null>(null)
const deleteCategoriaTarget = ref<Categoria | null>(null)
const deleteProductoTarget = ref<Producto | null>(null)
const categoriaFormRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const productoFormRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const precioFormRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const defaultCategoriaForm = () => ({
  codigo: '',
  nombre: '',
  descripcion: '',
  activo: true,
})

const defaultProductoForm = () => ({
  codigo: '',
  codigo_barras: '',
  nombre: '',
  descripcion: '',
  categoria_id: null as number | null,
  marca_id: null as number | null,
  unidad_medida_id: null as number | null,
  precio_venta: null as number | null,
  activo: true,
})

const categoriaForm = reactive(defaultCategoriaForm())
const productoForm = reactive(defaultProductoForm())

const selectedCategoria = computed(() =>
  categorias.value.find((c) => c.id === selectedCategoriaId.value) ?? null,
)

const isDetailLoading = computed(() => isDetailTransition.value && !!selectedCategoriaId.value)

const productoCountByCategoria = computed(() => {
  const counts: Record<number, number> = {}
  for (const p of allProductos.value) {
    counts[p.categoria_id] = (counts[p.categoria_id] ?? 0) + 1
  }
  return counts
})

const productos = computed(() => {
  if (!selectedCategoriaId.value) return []
  return allProductos.value.filter((p) => p.categoria_id === selectedCategoriaId.value)
})

const productosActivos = computed(() => productos.value.filter((p) => p.activo).length)

const productosInactivos = computed(() => productos.value.length - productosActivos.value)

const precioPromedioCategoria = computed(() => {
  const conPrecio = productos.value.filter((p) => p.precio_actual != null && p.precio_actual > 0)
  if (!conPrecio.length) return null
  const sum = conPrecio.reduce((acc, p) => acc + (p.precio_actual ?? 0), 0)
  return sum / conPrecio.length
})

const filteredCategorias = computed(() => {
  const term = searchCategorias.value.trim().toLowerCase()
  if (!term) return categorias.value
  return categorias.value.filter((c) =>
    [c.codigo, c.nombre, c.descripcion].some((v) => v?.toLowerCase().includes(term)),
  )
})

const marcaMap = computed(() => Object.fromEntries(marcas.value.map((m) => [m.id, m.nombre])))
const unidadMap = computed(() => Object.fromEntries(unidades.value.map((u) => [u.id, u])))

const editingProductoItem = computed(() =>
  editingProductoId.value
    ? allProductos.value.find((p) => p.id === editingProductoId.value) ?? null
    : null,
)

const precioVariacion = computed(() => {
  if (!precioTarget.value || nuevoPrecio.value == null || nuevoPrecio.value <= 0) return null
  const actual = precioTarget.value.precio_actual
  if (actual == null) return null
  const diff = nuevoPrecio.value - actual
  if (Math.abs(diff) < 0.005) return { diff: 0, pct: 0 }
  const pct = actual > 0 ? (diff / actual) * 100 : 0
  return { diff, pct }
})

const historialOrdenado = computed(() =>
  [...historialPrecios.value].sort(
    (a, b) => new Date(b.fecha_inicio).getTime() - new Date(a.fecha_inicio).getTime(),
  ),
)

const precioActivoHistorial = computed(() => historialPrecios.value.find((p) => p.activo) ?? null)

const productoHeaders = [
  { title: 'Imagen', key: 'imagen_url', sortable: false, width: 72 },
  { title: 'Código', key: 'codigo', width: 120 },
  { title: 'Cód. barras', key: 'codigo_barras', width: 130 },
  { title: 'Producto', key: 'nombre' },
  { title: 'Precio', key: 'precio_actual', width: 110 },
  { title: 'Marca', key: 'marca_id', sortable: false },
  { title: 'Unidad', key: 'unidad_medida_id', sortable: false, width: 100 },
  { title: 'Estado', key: 'activo', width: 110 },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 180 },
]

function productoImageUrl(url?: string | null) {
  if (!url) return null
  if (url.startsWith('http')) return url
  return `${API_BASE}${url}`
}

function formatPrecio(value?: number | null) {
  if (value == null) return '—'
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(value)
}

function formatFecha(value?: string | null) {
  if (!value) return '—'
  return new Date(value).toLocaleString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatFechaCorta(value?: string | null) {
  if (!value) return 'Vigente'
  return new Date(value).toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const precioPositivoRule = (v: unknown) => (v != null && Number(v) > 0) || 'Debe ser mayor a 0'

function ensureSelection() {
  if (!categorias.value.length) {
    selectedCategoriaId.value = null
    return
  }
  const stillExists = categorias.value.some((c) => c.id === selectedCategoriaId.value)
  if (!stillExists) {
    selectedCategoriaId.value = categorias.value[0].id
  }
}

async function loadCategorias() {
  loadingCategorias.value = true
  try {
    categorias.value = (await catalogosService.getCategorias()).data
    ensureSelection()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loadingCategorias.value = false
  }
}

async function loadProductos() {
  loadingProductos.value = true
  try {
    allProductos.value = (await catalogosService.getProductos()).data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loadingProductos.value = false
  }
}

async function loadCatalogos() {
  loadingProductos.value = true
  try {
    const [productosRes, marcasRes, unidadesRes] = await Promise.all([
      catalogosService.getProductos(),
      catalogosService.getMarcas(),
      catalogosService.getUnidadesMedida(),
    ])
    allProductos.value = productosRes.data
    marcas.value = marcasRes.data
    unidades.value = unidadesRes.data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loadingProductos.value = false
  }
}

function selectCategoria(categoria: Categoria) {
  if (selectedCategoriaId.value === categoria.id) return
  selectedCategoriaId.value = categoria.id
}

function openCreateCategoria() {
  editingCategoriaId.value = null
  Object.assign(categoriaForm, defaultCategoriaForm())
  categoriaDialog.value = true
}

function openEditCategoria(item?: Categoria) {
  const target = item ?? selectedCategoria.value
  if (!target) return
  editingCategoriaId.value = target.id
  Object.assign(categoriaForm, {
    codigo: target.codigo,
    nombre: target.nombre,
    descripcion: target.descripcion ?? '',
    activo: target.activo,
  })
  categoriaDialog.value = true
}

function openDeleteCategoria(item?: Categoria) {
  const target = item ?? selectedCategoria.value
  if (!target) return
  deleteCategoriaTarget.value = target
  confirmCategoriaOpen.value = true
}

async function saveCategoria() {
  if (!(await categoriaFormRef.value?.validate())?.valid) return
  const wasCreate = !editingCategoriaId.value
  savingCategoria.value = true
  try {
    const payload = {
      codigo: categoriaForm.codigo.trim(),
      nombre: categoriaForm.nombre.trim(),
      descripcion: categoriaForm.descripcion.trim() || null,
      activo: categoriaForm.activo,
    }
    if (editingCategoriaId.value) {
      await catalogosService.updateCategoria(editingCategoriaId.value, payload)
      appStore.showSuccess('Categoría actualizada')
    } else {
      const { data } = await catalogosService.createCategoria(payload)
      selectedCategoriaId.value = data.id
      appStore.showSuccess('Categoría creada')
    }
    categoriaDialog.value = false
    await loadCategorias()
    if (wasCreate) await loadProductos()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    savingCategoria.value = false
  }
}

async function confirmDeleteCategoria() {
  if (!deleteCategoriaTarget.value) return
  deletingCategoria.value = true
  try {
    const deletedId = deleteCategoriaTarget.value.id
    await catalogosService.deleteCategoria(deletedId)
    if (selectedCategoriaId.value === deletedId) {
      selectedCategoriaId.value = null
    }
    appStore.showSuccess('Categoría eliminada')
    confirmCategoriaOpen.value = false
    await Promise.all([loadCategorias(), loadProductos()])
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    deletingCategoria.value = false
  }
}

function resetFormImagen() {
  if (formImagenPreview.value) URL.revokeObjectURL(formImagenPreview.value)
  formImagenFile.value = null
  formImagenPreview.value = null
}

function openCreateProducto() {
  if (!selectedCategoriaId.value) return
  editingProductoId.value = null
  Object.assign(productoForm, {
    ...defaultProductoForm(),
    categoria_id: selectedCategoriaId.value,
  })
  resetFormImagen()
  productoDialog.value = true
}

function openEditProducto(item: Producto) {
  editingProductoId.value = item.id
  Object.assign(productoForm, {
    codigo: item.codigo,
    codigo_barras: item.codigo_barras ?? '',
    nombre: item.nombre,
    descripcion: item.descripcion ?? '',
    categoria_id: item.categoria_id,
    marca_id: item.marca_id,
    unidad_medida_id: item.unidad_medida_id,
    precio_venta: null,
    activo: item.activo,
  })
  resetFormImagen()
  productoDialog.value = true
}

function triggerFormImagenUpload() {
  formImagenInputRef.value?.click()
}

function onFormImagenSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return

  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowed.includes(file.type)) {
    appStore.showError('Formato no permitido. Use JPG, PNG o WEBP')
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    appStore.showError('La imagen no debe superar 2MB')
    return
  }

  if (formImagenPreview.value) URL.revokeObjectURL(formImagenPreview.value)
  formImagenFile.value = file
  formImagenPreview.value = URL.createObjectURL(file)
}

function quitarFormImagen() {
  resetFormImagen()
}

function openDeleteProducto(item: Producto) {
  deleteProductoTarget.value = item
  confirmProductoOpen.value = true
}

async function saveProducto() {
  if (!(await productoFormRef.value?.validate())?.valid) return
  if (!productoForm.categoria_id || !productoForm.unidad_medida_id) {
    appStore.showError('Seleccione unidad de medida')
    return
  }
  savingProducto.value = true
  try {
    const payload = {
      codigo: productoForm.codigo.trim(),
      codigo_barras: productoForm.codigo_barras.trim() || undefined,
      nombre: productoForm.nombre.trim(),
      descripcion: productoForm.descripcion.trim() || null,
      categoria_id: productoForm.categoria_id,
      marca_id: productoForm.marca_id,
      unidad_medida_id: productoForm.unidad_medida_id,
      activo: productoForm.activo,
      ...(editingProductoId.value
        ? {}
        : productoForm.precio_venta != null && productoForm.precio_venta > 0
          ? { precio_venta: productoForm.precio_venta }
          : {}),
    }
    let productoId = editingProductoId.value
    if (productoId) {
      await catalogosService.updateProducto(productoId, payload)
    } else {
      const { data } = await catalogosService.createProducto(payload)
      productoId = data.id
    }

    if (formImagenFile.value && productoId) {
      try {
        await catalogosService.uploadProductoImagen(productoId, formImagenFile.value)
      } catch (e) {
        appStore.showError(`Producto guardado, pero la imagen no se pudo subir: ${getErrorMessage(e)}`)
      }
    }

    appStore.showSuccess(editingProductoId.value ? 'Producto actualizado' : 'Producto creado')
    productoDialog.value = false
    resetFormImagen()
    await loadProductos()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    savingProducto.value = false
  }
}

async function confirmDeleteProducto() {
  if (!deleteProductoTarget.value) return
  deletingProducto.value = true
  try {
    await catalogosService.deleteProducto(deleteProductoTarget.value.id)
    appStore.showSuccess('Producto eliminado')
    confirmProductoOpen.value = false
    await loadProductos()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    deletingProducto.value = false
  }
}

function openCambiarPrecio(item: Producto) {
  precioTarget.value = item
  nuevoPrecio.value = item.precio_actual ?? null
  precioDialog.value = true
}

async function savePrecio() {
  if (!(await precioFormRef.value?.validate())?.valid) return
  if (!precioTarget.value || nuevoPrecio.value == null || nuevoPrecio.value <= 0) {
    appStore.showError('Ingrese un precio mayor a 0')
    return
  }
  savingPrecio.value = true
  try {
    await catalogosService.crearPrecioProducto(precioTarget.value.id, {
      precio_venta: nuevoPrecio.value,
    })
    appStore.showSuccess('Precio actualizado')
    precioDialog.value = false
    await loadProductos()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    savingPrecio.value = false
  }
}

async function openHistorialPrecios(item: Producto) {
  historialTarget.value = item
  historialDialog.value = true
  loadingHistorial.value = true
  try {
    historialPrecios.value = (await catalogosService.obtenerPreciosProducto(item.id)).data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
    historialPrecios.value = []
  } finally {
    loadingHistorial.value = false
  }
}

function triggerImagenUpload(item: Producto) {
  imagenTarget.value = item
  imagenInputRef.value?.click()
}

async function onImagenSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file || !imagenTarget.value) return

  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowed.includes(file.type)) {
    appStore.showError('Formato no permitido. Use JPG, PNG o WEBP')
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    appStore.showError('La imagen no debe superar 2MB')
    return
  }

  uploadingImagen.value = true
  try {
    await catalogosService.uploadProductoImagen(imagenTarget.value.id, file)
    appStore.showSuccess('Imagen actualizada')
    await loadProductos()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    uploadingImagen.value = false
    imagenTarget.value = null
  }
}

watch(selectedCategoriaId, (newId, oldId) => {
  if (newId === oldId || oldId == null) return
  isDetailTransition.value = true
  setTimeout(() => {
    isDetailTransition.value = false
  }, 200)
})

watch(productoDialog, (isOpen) => {
  if (!isOpen) resetFormImagen()
})

onMounted(async () => {
  isDetailTransition.value = true
  await Promise.all([loadCategorias(), loadCatalogos()])
  isDetailTransition.value = false
})
</script>

<template>
  <div>
    <PageHeader
      title="Catálogo de productos"
      subtitle="Organiza categorías y gestiona los productos de cada una"
      icon="mdi-package-variant-closed"
    />

    <v-card class="master-detail" elevation="0" border>
      <v-row no-gutters>
        <!-- Maestro: Categorías -->
        <v-col cols="12" md="4" lg="3" class="master-panel">
          <div class="master-panel__header pa-4">
            <div class="d-flex align-center justify-space-between mb-1">
              <div>
                <div class="text-subtitle-1 font-weight-bold">Categorías</div>
                <div class="text-caption text-medium-emphasis">{{ categorias.length }} registrada(s)</div>
              </div>
              <v-btn
                icon="mdi-plus"
                size="small"
                color="primary"
                variant="tonal"
                aria-label="Nueva categoría"
                @click="openCreateCategoria"
              />
            </div>
            <v-text-field
              v-model="searchCategorias"
              label="Buscar categoría..."
              prepend-inner-icon="mdi-magnify"
              clearable
              hide-details
              density="compact"
              class="mt-2"
              bg-color="surface"
            />
          </div>

          <v-divider />

          <div v-if="loadingCategorias" class="pa-4">
            <v-skeleton-loader type="list-item-two-line@4" />
          </div>

          <v-list v-else-if="filteredCategorias.length" nav density="comfortable" class="master-list py-2">
            <v-list-item
              v-for="categoria in filteredCategorias"
              :key="categoria.id"
              :value="categoria.id"
              :active="selectedCategoriaId === categoria.id"
              rounded="lg"
              class="master-list__item mx-2 mb-1"
              @click="selectCategoria(categoria)"
            >
              <template #prepend>
                <v-avatar
                  :color="selectedCategoriaId === categoria.id ? 'primary' : 'grey-lighten-3'"
                  size="40"
                  rounded="lg"
                >
                  <v-icon
                    :icon="selectedCategoriaId === categoria.id ? 'mdi-shape' : 'mdi-shape-outline'"
                    :color="selectedCategoriaId === categoria.id ? 'white' : undefined"
                    size="20"
                  />
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">{{ categoria.nombre }}</v-list-item-title>
              <v-list-item-subtitle>{{ categoria.codigo }}</v-list-item-subtitle>

              <template #append>
                <div class="d-flex align-center ga-1" @click.stop>
                  <v-progress-circular
                    v-if="selectedCategoriaId === categoria.id && loadingProductos"
                    indeterminate
                    size="16"
                    width="2"
                    color="primary"
                  />
                  <v-chip
                    v-else
                    size="x-small"
                    variant="tonal"
                    :color="productoCountByCategoria[categoria.id] ? 'primary' : 'default'"
                  >
                    {{ productoCountByCategoria[categoria.id] ?? 0 }}
                  </v-chip>
                  <v-chip :color="categoria.activo ? 'success' : 'error'" size="x-small" variant="tonal">
                    {{ categoria.activo ? 'Activa' : 'Inactiva' }}
                  </v-chip>
                  <v-menu location="bottom end">
                    <template #activator="{ props: menuProps }">
                      <v-btn
                        v-bind="menuProps"
                        icon="mdi-dots-vertical"
                        size="x-small"
                        variant="text"
                        aria-label="Acciones de categoría"
                      />
                    </template>
                    <v-list density="compact" min-width="160">
                      <v-list-item
                        prepend-icon="mdi-pencil-outline"
                        title="Editar"
                        @click="openEditCategoria(categoria)"
                      />
                      <v-list-item
                        prepend-icon="mdi-delete-outline"
                        title="Eliminar"
                        base-color="error"
                        @click="openDeleteCategoria(categoria)"
                      />
                    </v-list>
                  </v-menu>
                </div>
              </template>
            </v-list-item>
          </v-list>

          <div v-else class="empty-master pa-8 text-center">
            <v-icon icon="mdi-shape-off" size="48" color="grey-lighten-1" class="mb-3" />
            <div class="text-subtitle-2 font-weight-medium">Sin categorías</div>
            <div class="text-body-2 text-medium-emphasis mt-1 mb-4">
              {{ searchCategorias ? 'No hay coincidencias.' : 'Crea la primera categoría para comenzar.' }}
            </div>
            <v-btn
              v-if="!searchCategorias"
              color="primary"
              size="small"
              prepend-icon="mdi-plus"
              @click="openCreateCategoria"
            >
              Nueva categoría
            </v-btn>
          </div>
        </v-col>

        <v-divider vertical class="d-none d-md-flex" />

        <!-- Detalle: Productos -->
        <v-col cols="12" md="8" lg="9" class="detail-panel">
          <template v-if="selectedCategoria">
            <v-progress-linear
              v-if="isDetailLoading"
              indeterminate
              color="primary"
              height="3"
              class="detail-progress"
            />

            <div :key="selectedCategoria.id" class="detail-content">
              <div class="detail-inner">
                <!-- Hero compacto -->
                <v-card class="detail-hero" elevation="0" rounded="xl">
                  <div class="detail-hero__banner">
                    <div class="detail-hero__main">
                      <v-avatar color="white" size="56" rounded="lg" class="detail-hero__avatar">
                        <v-icon icon="mdi-shape" color="primary" size="28" />
                      </v-avatar>
                      <div class="detail-hero__text min-w-0">
                        <div class="d-flex align-center ga-2 flex-wrap">
                          <h2 class="detail-hero__title text-truncate">{{ selectedCategoria.nombre }}</h2>
                          <v-chip
                            :color="selectedCategoria.activo ? 'success' : 'error'"
                            size="x-small"
                            variant="flat"
                            class="detail-hero__status"
                          >
                            {{ selectedCategoria.activo ? 'Activa' : 'Inactiva' }}
                          </v-chip>
                        </div>
                        <div class="detail-hero__meta">
                          <span><v-icon icon="mdi-barcode" size="14" /> {{ selectedCategoria.codigo }}</span>
                          <span v-if="selectedCategoria.descripcion" class="detail-hero__desc text-truncate">
                            {{ selectedCategoria.descripcion }}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div class="detail-hero__actions">
                      <v-btn
                        size="small"
                        color="white"
                        variant="flat"
                        prepend-icon="mdi-plus"
                        :disabled="isDetailLoading"
                        @click="openCreateProducto"
                      >
                        Producto
                      </v-btn>
                      <v-menu location="bottom end">
                        <template #activator="{ props: menuProps }">
                          <v-btn
                            v-bind="menuProps"
                            icon="mdi-dots-vertical"
                            size="small"
                            variant="text"
                            color="white"
                            :disabled="isDetailLoading"
                            aria-label="Acciones de categoría"
                          />
                        </template>
                        <v-list density="compact" min-width="180">
                          <v-list-item
                            prepend-icon="mdi-pencil-outline"
                            title="Editar categoría"
                            @click="openEditCategoria()"
                          />
                          <v-list-item
                            prepend-icon="mdi-delete-outline"
                            title="Eliminar categoría"
                            base-color="error"
                            @click="openDeleteCategoria()"
                          />
                        </v-list>
                      </v-menu>
                    </div>
                  </div>

                  <!-- Stats -->
                  <div class="detail-stats">
                    <div class="detail-stat">
                      <v-icon icon="mdi-package-variant-closed" size="20" color="primary" class="mb-1" />
                      <div class="detail-stat__value">
                        <v-skeleton-loader v-if="isDetailLoading" type="text" width="32" />
                        <span v-else>{{ productos.length }}</span>
                      </div>
                      <div class="detail-stat__label">Total</div>
                    </div>
                    <div class="detail-stat">
                      <v-icon icon="mdi-check-circle-outline" size="20" color="success" class="mb-1" />
                      <div class="detail-stat__value">
                        <v-skeleton-loader v-if="isDetailLoading" type="text" width="32" />
                        <span v-else>{{ productosActivos }}</span>
                      </div>
                      <div class="detail-stat__label">Activos</div>
                    </div>
                    <div class="detail-stat">
                      <v-icon icon="mdi-close-circle-outline" size="20" color="error" class="mb-1" />
                      <div class="detail-stat__value">
                        <v-skeleton-loader v-if="isDetailLoading" type="text" width="32" />
                        <span v-else>{{ productosInactivos }}</span>
                      </div>
                      <div class="detail-stat__label">Inactivos</div>
                    </div>
                    <div class="detail-stat">
                      <v-icon icon="mdi-currency-usd" size="20" color="warning" class="mb-1" />
                      <div class="detail-stat__value detail-stat__value--price">
                        <v-skeleton-loader v-if="isDetailLoading" type="text" width="56" />
                        <span v-else>{{ formatPrecio(precioPromedioCategoria) }}</span>
                      </div>
                      <div class="detail-stat__label">Precio prom.</div>
                    </div>
                  </div>
                </v-card>

                <!-- Tabla de productos -->
                <div class="detail-table-wrap">
                  <div v-if="isDetailLoading" class="detail-skeleton pa-5">
                    <div class="d-flex align-center justify-space-between mb-4">
                      <v-skeleton-loader type="heading" width="180" />
                      <v-skeleton-loader type="button" width="140" />
                    </div>
                    <v-skeleton-loader type="text" width="260" class="mb-4" />
                    <v-skeleton-loader type="table-row@5" />
                  </div>

                  <v-fade-transition mode="out-in">
                    <div v-if="!isDetailLoading" class="detail-products">
                      <BaseDataTable
                        v-model:search="searchProductos"
                        :items="productos"
                        :headers="productoHeaders"
                        :loading="loadingProductos"
                        title="Productos"
                        search-label="Buscar por nombre, código o marca..."
                        empty-icon="mdi-package-variant-closed-remove"
                        empty-title="Sin productos en esta categoría"
                        empty-subtitle="Agrega el primer producto con el botón de arriba."
                      >
                        <template #toolbar>
                          <v-chip size="small" variant="tonal" color="primary" prepend-icon="mdi-filter-outline">
                            {{ productos.length }} registro(s)
                          </v-chip>
                        </template>

                        <template #item.imagen_url="{ item }">
                          <v-avatar size="40" rounded="lg" color="grey-lighten-3">
                            <v-img v-if="item.imagen_url" :src="productoImageUrl(item.imagen_url)!" cover />
                            <v-icon v-else icon="mdi-image-off-outline" size="20" color="grey" />
                          </v-avatar>
                        </template>

                        <template #item.codigo="{ value }">
                          <span class="text-body-2 font-weight-medium">{{ value }}</span>
                        </template>

                        <template #item.codigo_barras="{ value }">
                          <span v-if="value" class="text-body-2 text-medium-emphasis">{{ value }}</span>
                          <span v-else class="text-medium-emphasis">—</span>
                        </template>

                        <template #item.nombre="{ item }">
                          <div class="min-w-0 py-1">
                            <div class="font-weight-medium text-truncate">{{ item.nombre }}</div>
                            <div v-if="item.descripcion" class="text-caption text-medium-emphasis text-truncate">
                              {{ item.descripcion }}
                            </div>
                          </div>
                        </template>

                        <template #item.precio_actual="{ value }">
                          <span class="detail-price-cell">{{ formatPrecio(value) }}</span>
                        </template>

                        <template #item.marca_id="{ value }">
                          <v-chip v-if="value" size="x-small" variant="tonal" color="secondary">
                            {{ marcaMap[value] ?? value }}
                          </v-chip>
                          <span v-else class="text-medium-emphasis">—</span>
                        </template>

                        <template #item.unidad_medida_id="{ value }">
                          <span class="text-body-2">{{ unidadMap[value]?.abreviatura ?? value }}</span>
                        </template>

                        <template #item.activo="{ value }">
                          <v-chip :color="value ? 'success' : 'error'" size="x-small" variant="tonal">
                            {{ value ? 'Activo' : 'Inactivo' }}
                          </v-chip>
                        </template>

                        <template #item.actions="{ item }">
                          <div class="detail-row-actions">
                            <v-tooltip text="Subir imagen" location="top">
                              <template #activator="{ props }">
                                <v-btn
                                  v-bind="props"
                                  icon="mdi-camera-outline"
                                  size="x-small"
                                  variant="text"
                                  :loading="uploadingImagen && imagenTarget?.id === item.id"
                                  @click="triggerImagenUpload(item)"
                                />
                              </template>
                            </v-tooltip>
                            <v-tooltip text="Cambiar precio" location="top">
                              <template #activator="{ props }">
                                <v-btn
                                  v-bind="props"
                                  icon="mdi-currency-usd"
                                  size="x-small"
                                  variant="text"
                                  @click="openCambiarPrecio(item)"
                                />
                              </template>
                            </v-tooltip>
                            <v-tooltip text="Historial" location="top">
                              <template #activator="{ props }">
                                <v-btn
                                  v-bind="props"
                                  icon="mdi-history"
                                  size="x-small"
                                  variant="text"
                                  @click="openHistorialPrecios(item)"
                                />
                              </template>
                            </v-tooltip>
                            <v-menu location="bottom end">
                              <template #activator="{ props: menuProps }">
                                <v-btn
                                  v-bind="menuProps"
                                  icon="mdi-dots-vertical"
                                  size="x-small"
                                  variant="text"
                                  aria-label="Más acciones"
                                />
                              </template>
                              <v-list density="compact" min-width="160">
                                <v-list-item
                                  prepend-icon="mdi-pencil-outline"
                                  title="Editar"
                                  @click="openEditProducto(item)"
                                />
                                <v-list-item
                                  prepend-icon="mdi-delete-outline"
                                  title="Eliminar"
                                  base-color="error"
                                  @click="openDeleteProducto(item)"
                                />
                              </v-list>
                            </v-menu>
                          </div>
                        </template>
                      </BaseDataTable>
                    </div>
                  </v-fade-transition>
                </div>
              </div>
            </div>
          </template>

          <div v-else class="detail-empty">
            <div class="detail-empty__card">
              <div class="detail-empty__icon-wrap">
                <v-icon icon="mdi-folder-open-outline" size="40" color="primary" />
              </div>
              <div class="text-h6 font-weight-bold mt-4">Selecciona una categoría</div>
              <div class="text-body-2 text-medium-emphasis mt-2 mb-6">
                Elige una categoría del panel izquierdo para ver y gestionar sus productos.
              </div>
              <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateCategoria">
                Crear categoría
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card>

    <v-dialog v-model="categoriaDialog" max-width="560" persistent>
      <v-card>
        <v-card-title class="pa-5 pb-2">
          <div class="text-h6">{{ editingCategoriaId ? 'Editar categoría' : 'Nueva categoría' }}</div>
        </v-card-title>
        <v-card-text class="pa-5 pt-2">
          <v-form ref="categoriaFormRef">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="categoriaForm.codigo" label="Código" :rules="[requiredRule]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="categoriaForm.nombre" label="Nombre" :rules="[requiredRule]" />
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="categoriaForm.descripcion" label="Descripción" rows="2" />
              </v-col>
              <v-col cols="12">
                <v-switch v-model="categoriaForm.activo" label="Activa" color="success" hide-details inset />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" @click="categoriaDialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="flat" :loading="savingCategoria" @click="saveCategoria">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="productoDialog" max-width="720" persistent scrollable>
      <v-card class="form-dialog">
        <div class="form-dialog__header form-dialog__header--product">
          <div class="d-flex align-center ga-3">
            <v-avatar color="white" size="48" rounded="lg">
              <v-icon
                :icon="editingProductoId ? 'mdi-pencil-outline' : 'mdi-package-variant-plus'"
                color="primary"
              />
            </v-avatar>
            <div class="min-w-0">
              <div class="text-h6 font-weight-bold">
                {{ editingProductoId ? 'Editar producto' : 'Nuevo producto' }}
              </div>
              <div v-if="selectedCategoria" class="text-body-2 form-dialog__subtitle">
                {{ selectedCategoria.nombre }} · {{ selectedCategoria.codigo }}
              </div>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="productoDialog = false" />
        </div>

        <v-divider />

        <v-card-text class="pa-5">
          <v-form ref="productoFormRef">
            <section class="form-section">
              <div class="form-section__title">
                <v-icon icon="mdi-image-outline" size="18" class="mr-2" />
                Imagen del producto
              </div>
              <div class="imagen-panel">
                <div class="imagen-panel__preview">
                  <v-img
                    v-if="formImagenPreview || (editingProductoId && editingProductoItem?.imagen_url)"
                    :src="formImagenPreview ?? productoImageUrl(editingProductoItem?.imagen_url)!"
                    cover
                  />
                  <v-icon v-else icon="mdi-image-off-outline" size="32" color="grey-lighten-1" />
                </div>
                <div class="imagen-panel__actions">
                  <v-btn
                    size="small"
                    variant="outlined"
                    prepend-icon="mdi-upload"
                    @click="triggerFormImagenUpload"
                  >
                    {{ formImagenPreview ? 'Cambiar imagen' : 'Seleccionar imagen' }}
                  </v-btn>
                  <v-btn
                    v-if="formImagenPreview"
                    size="small"
                    variant="text"
                    color="error"
                    prepend-icon="mdi-close"
                    @click="quitarFormImagen"
                  >
                    Quitar
                  </v-btn>
                  <div class="text-caption text-medium-emphasis mt-1">
                    JPG, PNG o WEBP. Máx. 2MB.
                    <template v-if="!editingProductoId">Se subirá al crear el producto.</template>
                  </div>
                </div>
                <input
                  ref="formImagenInputRef"
                  type="file"
                  accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
                  class="d-none"
                  @change="onFormImagenSelected"
                />
              </div>
            </section>

            <section class="form-section">
              <div class="form-section__title">
                <v-icon icon="mdi-identifier" size="18" class="mr-2" />
                Información general
              </div>
              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="productoForm.codigo"
                    label="Código"
                    placeholder="Ej. PROD-001"
                    prepend-inner-icon="mdi-barcode"
                    :rules="[requiredRule]"
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="productoForm.nombre"
                    label="Nombre del producto"
                    placeholder="Nombre comercial"
                    prepend-inner-icon="mdi-tag-text-outline"
                    :rules="[requiredRule]"
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="productoForm.codigo_barras"
                    label="Código de barras"
                    placeholder="Opcional"
                    prepend-inner-icon="mdi-barcode-scan"
                    variant="outlined"
                    density="comfortable"
                    clearable
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-if="!editingProductoId"
                    v-model.number="productoForm.precio_venta"
                    label="Precio inicial"
                    placeholder="0.00"
                    type="number"
                    min="0"
                    step="0.01"
                    prefix="$"
                    prepend-inner-icon="mdi-currency-usd"
                    hint="Opcional. Puedes definirlo después."
                    persistent-hint
                    variant="outlined"
                    density="comfortable"
                  />
                  <v-text-field
                    v-else
                    :model-value="formatPrecio(editingProductoItem?.precio_actual)"
                    label="Precio actual"
                    prepend-inner-icon="mdi-currency-usd"
                    hint="Usa «Cambiar precio» en la tabla para actualizarlo."
                    persistent-hint
                    variant="outlined"
                    density="comfortable"
                    readonly
                    bg-color="grey-lighten-4"
                  />
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="productoForm.descripcion"
                    label="Descripción"
                    placeholder="Detalles, presentación o notas del producto"
                    prepend-inner-icon="mdi-text-box-outline"
                    rows="2"
                    auto-grow
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>
              </v-row>
            </section>

            <section class="form-section">
              <div class="form-section__title">
                <v-icon icon="mdi-shape-outline" size="18" class="mr-2" />
                Clasificación
              </div>
              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="productoForm.marca_id"
                    :items="marcas"
                    item-title="nombre"
                    item-value="id"
                    label="Marca"
                    placeholder="Sin marca"
                    prepend-inner-icon="mdi-bookmark-outline"
                    clearable
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="productoForm.unidad_medida_id"
                    :items="unidades"
                    item-title="nombre"
                    item-value="id"
                    label="Unidad de medida"
                    prepend-inner-icon="mdi-ruler"
                    :rules="[requiredRule]"
                    variant="outlined"
                    density="comfortable"
                  >
                    <template #item="{ props, item }">
                      <v-list-item v-bind="props" :subtitle="item.raw.abreviatura" />
                    </template>
                    <template #selection="{ item }">
                      {{ item.raw.nombre }} ({{ item.raw.abreviatura }})
                    </template>
                  </v-select>
                </v-col>
              </v-row>
            </section>

            <section class="form-section form-section--last">
              <div class="form-section__title">
                <v-icon icon="mdi-toggle-switch-outline" size="18" class="mr-2" />
                Disponibilidad
              </div>
              <div class="status-panel">
                <div class="status-panel__info">
                  <div class="font-weight-medium">Estado del producto</div>
                  <div class="text-body-2 text-medium-emphasis">
                    {{
                      productoForm.activo
                        ? 'Visible y disponible en operaciones.'
                        : 'Oculto y no disponible para venta.'
                    }}
                  </div>
                </div>
                <v-switch
                  v-model="productoForm.activo"
                  :label="productoForm.activo ? 'Activo' : 'Inactivo'"
                  :color="productoForm.activo ? 'success' : 'error'"
                  hide-details
                  inset
                />
              </div>
            </section>
          </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions class="form-dialog__actions">
          <v-btn variant="text" @click="productoDialog = false">Cancelar</v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            variant="flat"
            prepend-icon="mdi-content-save-outline"
            :loading="savingProducto"
            @click="saveProducto"
          >
            {{ editingProductoId ? 'Guardar cambios' : 'Crear producto' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <ConfirmDialog
      v-model="confirmCategoriaOpen"
      :loading="deletingCategoria"
      :message="`¿Eliminar la categoría «${deleteCategoriaTarget?.nombre}» y sus productos asociados?`"
      @confirm="confirmDeleteCategoria"
    />

    <ConfirmDialog
      v-model="confirmProductoOpen"
      :loading="deletingProducto"
      :message="`¿Eliminar el producto «${deleteProductoTarget?.nombre}»?`"
      @confirm="confirmDeleteProducto"
    />

    <input
      ref="imagenInputRef"
      type="file"
      accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
      class="d-none"
      @change="onImagenSelected"
    />

    <v-dialog v-model="precioDialog" max-width="480" persistent>
      <v-card class="form-dialog">
        <div class="form-dialog__header form-dialog__header--price">
          <div class="d-flex align-center ga-3">
            <v-avatar color="white" size="48" rounded="lg">
              <v-icon icon="mdi-currency-usd" color="warning" />
            </v-avatar>
            <div class="min-w-0">
              <div class="text-h6 font-weight-bold">Actualizar precio</div>
              <div v-if="precioTarget" class="text-body-2 form-dialog__subtitle text-truncate">
                {{ precioTarget.nombre }}
              </div>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="precioDialog = false" />
        </div>

        <v-divider />

        <v-card-text class="pa-5">
          <div v-if="precioTarget" class="price-product-card mb-5">
            <v-avatar size="52" rounded="lg" color="grey-lighten-3" class="flex-shrink-0">
              <v-img v-if="precioTarget.imagen_url" :src="productoImageUrl(precioTarget.imagen_url)!" cover />
              <v-icon v-else icon="mdi-package-variant" color="grey" />
            </v-avatar>
            <div class="min-w-0 flex-grow-1">
              <div class="font-weight-medium text-truncate">{{ precioTarget.nombre }}</div>
              <div class="text-caption text-medium-emphasis">{{ precioTarget.codigo }}</div>
            </div>
            <div class="price-product-card__current text-right">
              <div class="text-caption text-medium-emphasis">Precio actual</div>
              <div class="text-h6 font-weight-bold">
                {{ formatPrecio(precioTarget.precio_actual) }}
              </div>
            </div>
          </div>

          <v-form ref="precioFormRef">
            <v-text-field
              v-model.number="nuevoPrecio"
              label="Nuevo precio de venta"
              type="number"
              min="0.01"
              step="0.01"
              prefix="$"
              prepend-inner-icon="mdi-cash-plus"
              placeholder="0.00"
              :rules="[precioPositivoRule]"
              variant="outlined"
              density="comfortable"
              autofocus
              class="price-input-field"
            />
          </v-form>

          <v-expand-transition>
            <div v-if="precioVariacion && precioVariacion.diff !== 0" class="price-diff-banner mt-4">
              <v-icon
                :icon="precioVariacion.diff > 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
                :color="precioVariacion.diff > 0 ? 'error' : 'success'"
                size="20"
                class="mr-2"
              />
              <span>
                {{ precioVariacion.diff > 0 ? 'Incremento' : 'Reducción' }} de
                <strong>{{ formatPrecio(Math.abs(precioVariacion.diff)) }}</strong>
                ({{ precioVariacion.pct > 0 ? '+' : '' }}{{ precioVariacion.pct.toFixed(1) }}%)
              </span>
            </div>
          </v-expand-transition>

          <v-alert type="info" variant="tonal" density="compact" class="mt-4 mb-0">
            El precio anterior quedará registrado en el historial.
          </v-alert>
        </v-card-text>

        <v-divider />

        <v-card-actions class="form-dialog__actions">
          <v-btn variant="text" @click="precioDialog = false">Cancelar</v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            variant="flat"
            prepend-icon="mdi-check"
            :loading="savingPrecio"
            @click="savePrecio"
          >
            Aplicar precio
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="historialDialog" max-width="560" scrollable>
      <v-card class="form-dialog">
        <div class="form-dialog__header form-dialog__header--history">
          <div class="d-flex align-center ga-3">
            <v-avatar color="white" size="48" rounded="lg">
              <v-icon icon="mdi-history" color="secondary" />
            </v-avatar>
            <div class="min-w-0">
              <div class="text-h6 font-weight-bold">Historial de precios</div>
              <div v-if="historialTarget" class="text-body-2 form-dialog__subtitle text-truncate">
                {{ historialTarget.nombre }}
              </div>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="historialDialog = false" />
        </div>

        <v-divider />

        <v-card-text class="pa-5">
          <div
            v-if="!loadingHistorial && historialTarget"
            class="history-summary mb-5"
          >
            <div>
              <div class="text-caption text-medium-emphasis">Precio vigente</div>
              <div class="text-h5 font-weight-bold">
                {{ formatPrecio(historialTarget.precio_actual ?? precioActivoHistorial?.precio_venta) }}
              </div>
            </div>
            <v-chip
              v-if="precioActivoHistorial"
              color="success"
              variant="tonal"
              size="small"
              prepend-icon="mdi-check-circle"
            >
              Desde {{ formatFechaCorta(precioActivoHistorial.fecha_inicio) }}
            </v-chip>
          </div>

          <v-skeleton-loader v-if="loadingHistorial" type="list-item-two-line@4" />

          <div v-else-if="historialOrdenado.length" class="history-timeline">
            <div
              v-for="(precio, index) in historialOrdenado"
              :key="precio.id"
              class="history-timeline__item"
              :class="{ 'history-timeline__item--active': precio.activo }"
            >
              <div class="history-timeline__marker">
                <div class="history-timeline__dot" />
                <div v-if="index < historialOrdenado.length - 1" class="history-timeline__line" />
              </div>
              <div class="history-timeline__content">
                <div class="d-flex align-center justify-space-between ga-2 flex-wrap">
                  <div class="text-h6 font-weight-bold">{{ formatPrecio(precio.precio_venta) }}</div>
                  <v-chip
                    :color="precio.activo ? 'success' : 'default'"
                    size="x-small"
                    variant="tonal"
                  >
                    {{ precio.activo ? 'Vigente' : 'Histórico' }}
                  </v-chip>
                </div>
                <div class="text-body-2 text-medium-emphasis mt-1">
                  <v-icon icon="mdi-calendar-start" size="14" class="mr-1" />
                  {{ formatFecha(precio.fecha_inicio) }}
                </div>
                <div v-if="precio.fecha_fin" class="text-body-2 text-medium-emphasis">
                  <v-icon icon="mdi-calendar-end" size="14" class="mr-1" />
                  {{ formatFecha(precio.fecha_fin) }}
                </div>
              </div>
            </div>
          </div>

          <div v-else class="history-empty">
            <v-icon icon="mdi-chart-timeline-variant" size="56" color="grey-lighten-1" class="mb-3" />
            <div class="text-subtitle-1 font-weight-medium">Sin historial</div>
            <div class="text-body-2 text-medium-emphasis mt-1">
              Aún no hay cambios de precio registrados para este producto.
            </div>
          </div>
        </v-card-text>

        <v-divider />

        <v-card-actions class="form-dialog__actions">
          <v-spacer />
          <v-btn variant="text" @click="historialDialog = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.master-detail {
  overflow: hidden;
  min-height: 520px;
}

.master-panel {
  background: rgba(var(--v-theme-primary), 0.02);
  min-height: 520px;
}

.master-list__item {
  cursor: pointer;
  transition: background 0.15s ease;
}

.master-list__item.v-list-item--active {
  background: rgba(var(--v-theme-primary), 0.12) !important;
}

.detail-panel {
  min-height: 520px;
  position: relative;
  background: rgba(var(--v-theme-on-surface), 0.025);
}

.detail-inner {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1200px;
}

.detail-hero {
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.detail-hero__banner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 20px 16px;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)), rgba(var(--v-theme-primary), 0.82));
  color: white;
}

.detail-hero__main {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  min-width: 0;
  flex: 1;
}

.detail-hero__avatar {
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.detail-hero__title {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.3;
  margin: 0;
  color: white;
}

.detail-hero__status {
  flex-shrink: 0;
}

.detail-hero__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  margin-top: 6px;
  font-size: 0.8125rem;
  opacity: 0.9;
}

.detail-hero__meta .v-icon {
  margin-right: 4px;
  vertical-align: -2px;
}

.detail-hero__desc {
  max-width: 360px;
  opacity: 0.85;
}

.detail-hero__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: rgba(var(--v-border-color), var(--v-border-opacity));
}

.detail-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 8px;
  background: rgb(var(--v-theme-surface));
  text-align: center;
}

.detail-stat__value {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.2;
}

.detail-stat__value--price {
  font-size: 0.9375rem;
}

.detail-stat__label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.55);
  margin-top: 2px;
}

.detail-table-wrap {
  min-height: 200px;
}

.detail-products :deep(.data-table-card) {
  border-radius: 16px;
  overflow: hidden;
}

.detail-products :deep(.card-toolbar) {
  padding-top: 16px !important;
  min-height: auto;
}

.detail-products :deep(.search-field) {
  max-width: 360px;
}

.detail-price-cell {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: rgb(var(--v-theme-primary));
}

.detail-row-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0;
  white-space: nowrap;
}

.detail-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 480px;
  padding: 32px 20px;
}

.detail-empty__card {
  text-align: center;
  max-width: 360px;
  padding: 40px 32px;
  border-radius: 20px;
  border: 1px dashed rgba(var(--v-border-color), calc(var(--v-border-opacity) * 2));
  background: rgb(var(--v-theme-surface));
}

.detail-empty__icon-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: rgba(var(--v-theme-primary), 0.08);
}

.detail-progress {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2;
}

.detail-content {
  animation: detail-enter 0.25s ease;
}

.detail-chip-skeleton :deep(.v-skeleton-loader__chip) {
  margin: 0;
}

.detail-skeleton {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

@keyframes detail-enter {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.detail-empty,
.empty-master {
  color: rgba(var(--v-theme-on-surface), 0.7);
}

.form-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 20px 20px 16px;
}

.form-dialog__header--product {
  background: linear-gradient(135deg, rgba(var(--v-theme-primary), 0.12), rgba(var(--v-theme-primary), 0.04));
}

.form-dialog__header--price {
  background: linear-gradient(135deg, rgba(var(--v-theme-warning), 0.16), rgba(var(--v-theme-warning), 0.04));
}

.form-dialog__header--history {
  background: linear-gradient(135deg, rgba(var(--v-theme-secondary), 0.14), rgba(var(--v-theme-secondary), 0.04));
}

.form-dialog__subtitle {
  opacity: 0.85;
}

.form-dialog__actions {
  padding: 16px 20px;
}

.form-section {
  margin-bottom: 24px;
}

.form-section--last {
  margin-bottom: 0;
}

.form-section__title {
  display: flex;
  align-items: center;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-bottom: 12px;
}

.status-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.imagen-panel {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.imagen-panel__preview {
  width: 88px;
  height: 88px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-on-surface), 0.05);
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.imagen-panel__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.price-product-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.price-product-card__current {
  flex-shrink: 0;
}

.price-diff-banner {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.875rem;
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.price-input-field :deep(input) {
  font-size: 1.125rem;
  font-weight: 600;
}

.history-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 16px;
  border-radius: 12px;
  background: rgba(var(--v-theme-success), 0.08);
  border: 1px solid rgba(var(--v-theme-success), 0.2);
}

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.history-timeline__item {
  display: flex;
  gap: 14px;
}

.history-timeline__marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 16px;
  flex-shrink: 0;
  padding-top: 6px;
}

.history-timeline__dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(var(--v-theme-on-surface), 0.25);
  border: 2px solid rgb(var(--v-theme-surface));
  box-shadow: 0 0 0 1px rgba(var(--v-border-color), var(--v-border-opacity));
  flex-shrink: 0;
}

.history-timeline__item--active .history-timeline__dot {
  background: rgb(var(--v-theme-success));
  box-shadow: 0 0 0 3px rgba(var(--v-theme-success), 0.25);
}

.history-timeline__line {
  width: 2px;
  flex: 1;
  min-height: 24px;
  margin: 4px 0;
  background: rgba(var(--v-border-color), var(--v-border-opacity));
}

.history-timeline__content {
  flex: 1;
  padding-bottom: 20px;
  min-width: 0;
}

.history-timeline__item--active .history-timeline__content {
  padding-bottom: 16px;
}

.history-empty {
  text-align: center;
  padding: 32px 16px;
}

@media (max-width: 960px) {
  .master-panel {
    border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    max-height: 320px;
    overflow-y: auto;
  }

  .detail-inner {
    padding: 12px;
  }

  .detail-hero__banner {
    flex-direction: column;
    align-items: stretch;
  }

  .detail-hero__actions {
    justify-content: flex-end;
  }

  .detail-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .detail-products :deep(.search-field) {
    max-width: 100%;
  }
}
</style>
