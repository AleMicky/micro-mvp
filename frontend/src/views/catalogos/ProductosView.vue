<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import PageHeader from '@/components/PageHeader.vue'
import { catalogosService } from '@/services/catalogos.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import { requiredRule } from '@/utils/validation'
import type { Categoria, Marca, Producto, UnidadMedida } from '@/types/catalogos.types'

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

const defaultCategoriaForm = () => ({
  codigo: '',
  nombre: '',
  descripcion: '',
  activo: true,
})

const defaultProductoForm = () => ({
  codigo: '',
  nombre: '',
  descripcion: '',
  categoria_id: null as number | null,
  marca_id: null as number | null,
  unidad_medida_id: null as number | null,
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

const filteredCategorias = computed(() => {
  const term = searchCategorias.value.trim().toLowerCase()
  if (!term) return categorias.value
  return categorias.value.filter((c) =>
    [c.codigo, c.nombre, c.descripcion].some((v) => v?.toLowerCase().includes(term)),
  )
})

const marcaMap = computed(() => Object.fromEntries(marcas.value.map((m) => [m.id, m.nombre])))
const unidadMap = computed(() => Object.fromEntries(unidades.value.map((u) => [u.id, u])))

const productoHeaders = [
  { title: 'Código', key: 'codigo', width: 120 },
  { title: 'Producto', key: 'nombre' },
  { title: 'Marca', key: 'marca_id', sortable: false },
  { title: 'Unidad', key: 'unidad_medida_id', sortable: false, width: 100 },
  { title: 'Estado', key: 'activo', width: 110 },
  { title: 'Acciones', key: 'actions', sortable: false, align: 'end' as const, width: 120 },
]

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

function openCreateProducto() {
  if (!selectedCategoriaId.value) return
  editingProductoId.value = null
  Object.assign(productoForm, {
    ...defaultProductoForm(),
    categoria_id: selectedCategoriaId.value,
  })
  productoDialog.value = true
}

function openEditProducto(item: Producto) {
  editingProductoId.value = item.id
  Object.assign(productoForm, {
    codigo: item.codigo,
    nombre: item.nombre,
    descripcion: item.descripcion ?? '',
    categoria_id: item.categoria_id,
    marca_id: item.marca_id,
    unidad_medida_id: item.unidad_medida_id,
    activo: item.activo,
  })
  productoDialog.value = true
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
      nombre: productoForm.nombre.trim(),
      descripcion: productoForm.descripcion.trim() || null,
      categoria_id: productoForm.categoria_id,
      marca_id: productoForm.marca_id,
      unidad_medida_id: productoForm.unidad_medida_id,
      activo: productoForm.activo,
    }
    if (editingProductoId.value) {
      await catalogosService.updateProducto(editingProductoId.value, payload)
      appStore.showSuccess('Producto actualizado')
    } else {
      await catalogosService.createProducto(payload)
      appStore.showSuccess('Producto creado')
    }
    productoDialog.value = false
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

watch(selectedCategoriaId, (newId, oldId) => {
  if (newId === oldId || oldId == null) return
  isDetailTransition.value = true
  setTimeout(() => {
    isDetailTransition.value = false
  }, 200)
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
              <div class="detail-panel__header pa-5">
                <div class="d-flex align-start ga-3">
                  <v-avatar color="primary" size="52" rounded="lg" class="flex-shrink-0">
                    <v-icon icon="mdi-shape" color="white" />
                  </v-avatar>
                  <div class="flex-grow-1 min-w-0">
                    <div class="text-h6 font-weight-bold text-truncate">{{ selectedCategoria.nombre }}</div>
                    <div class="text-body-2 text-medium-emphasis d-flex flex-wrap ga-2 mt-1">
                      <span>
                        <v-icon icon="mdi-barcode" size="14" class="mr-1" />{{ selectedCategoria.codigo }}
                      </span>
                      <v-chip :color="selectedCategoria.activo ? 'success' : 'error'" size="x-small" variant="tonal">
                        {{ selectedCategoria.activo ? 'Activa' : 'Inactiva' }}
                      </v-chip>
                      <v-skeleton-loader
                        v-if="isDetailLoading"
                        type="chip"
                        width="120"
                        class="detail-chip-skeleton"
                      />
                      <v-chip v-else size="x-small" variant="outlined" prepend-icon="mdi-package-variant-closed">
                        {{ productos.length }} producto(s)
                      </v-chip>
                      <v-chip
                        v-if="!isDetailLoading && productos.length"
                        size="x-small"
                        variant="outlined"
                        color="success"
                        prepend-icon="mdi-check-circle-outline"
                      >
                        {{ productosActivos }} activo(s)
                      </v-chip>
                    </div>
                    <p v-if="selectedCategoria.descripcion" class="text-body-2 text-medium-emphasis mt-2 mb-0">
                      {{ selectedCategoria.descripcion }}
                    </p>
                  </div>
                </div>

                <div class="detail-toolbar mt-4">
                  <v-btn
                    size="small"
                    variant="tonal"
                    prepend-icon="mdi-pencil-outline"
                    :disabled="isDetailLoading"
                    @click="openEditCategoria()"
                  >
                    Editar categoría
                  </v-btn>
                  <v-btn
                    size="small"
                    variant="text"
                    color="error"
                    prepend-icon="mdi-delete-outline"
                    :disabled="isDetailLoading"
                    @click="openDeleteCategoria()"
                  >
                    Eliminar categoría
                  </v-btn>
                </div>
              </div>

              <v-divider />

              <div class="pa-5 pt-0 detail-table-area">
                <div v-if="isDetailLoading" class="detail-skeleton pa-5">
                  <div class="d-flex align-center justify-space-between mb-4">
                    <v-skeleton-loader type="heading" width="180" />
                    <v-skeleton-loader type="button" width="140" />
                  </div>
                  <v-skeleton-loader type="text" width="260" class="mb-4" />
                  <v-skeleton-loader type="table-row@5" />
                </div>

                <v-fade-transition mode="out-in">
                  <BaseDataTable
                    v-if="!isDetailLoading"
                    v-model:search="searchProductos"
                    :items="productos"
                    :headers="productoHeaders"
                    :loading="loadingProductos"
                    title="Productos"
                    :subtitle="`Artículos en la categoría ${selectedCategoria.nombre}`"
                    search-label="Buscar producto..."
                    empty-icon="mdi-package-variant-closed-remove"
                    empty-title="Sin productos"
                    empty-subtitle="Esta categoría aún no tiene productos registrados."
                  >
                    <template #actions>
                      <v-btn size="small" color="primary" prepend-icon="mdi-plus" @click="openCreateProducto">
                        Nuevo producto
                      </v-btn>
                    </template>

                    <template #item.nombre="{ item }">
                      <div class="d-flex align-center ga-2 py-1">
                        <v-avatar color="primary" variant="tonal" size="32" rounded="lg">
                          <v-icon icon="mdi-package-variant" size="16" />
                        </v-avatar>
                        <div class="min-w-0">
                          <div class="font-weight-medium text-truncate">{{ item.nombre }}</div>
                          <div v-if="item.descripcion" class="text-caption text-medium-emphasis text-truncate">
                            {{ item.descripcion }}
                          </div>
                        </div>
                      </div>
                    </template>

                    <template #item.marca_id="{ value }">
                      <v-chip v-if="value" size="small" variant="tonal" color="secondary">
                        {{ marcaMap[value] ?? value }}
                      </v-chip>
                      <span v-else class="text-medium-emphasis">—</span>
                    </template>

                    <template #item.unidad_medida_id="{ value }">
                      <v-chip size="small" variant="outlined">
                        {{ unidadMap[value]?.abreviatura ?? value }}
                      </v-chip>
                    </template>

                    <template #item.activo="{ value }">
                      <v-chip :color="value ? 'success' : 'error'" size="small" variant="tonal">
                        {{ value ? 'Activo' : 'Inactivo' }}
                      </v-chip>
                    </template>

                    <template #item.actions="{ item }">
                      <v-tooltip text="Editar" location="top">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            icon="mdi-pencil-outline"
                            size="small"
                            variant="text"
                            @click="openEditProducto(item)"
                          />
                        </template>
                      </v-tooltip>
                      <v-tooltip text="Eliminar" location="top">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            icon="mdi-delete-outline"
                            size="small"
                            variant="text"
                            color="error"
                            @click="openDeleteProducto(item)"
                          />
                        </template>
                      </v-tooltip>
                    </template>
                  </BaseDataTable>
                </v-fade-transition>
              </div>
            </div>
          </template>

          <div v-else class="detail-empty pa-12 text-center">
            <v-icon icon="mdi-cursor-default-click-outline" size="64" color="grey-lighten-1" class="mb-4" />
            <div class="text-h6 font-weight-medium">Selecciona una categoría</div>
            <div class="text-body-2 text-medium-emphasis mt-2 mb-6">
              Elige una categoría del listado o crea una nueva para gestionar sus productos.
            </div>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateCategoria">Nueva categoría</v-btn>
          </div>
        </v-col>
      </v-row>
    </v-card>

    <!-- Diálogo categoría -->
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

    <!-- Diálogo producto -->
    <v-dialog v-model="productoDialog" max-width="640" persistent scrollable>
      <v-card>
        <v-card-title class="pa-5 pb-2">
          <div class="text-h6">{{ editingProductoId ? 'Editar producto' : 'Nuevo producto' }}</div>
        </v-card-title>
        <v-card-text class="pa-5 pt-2">
          <v-alert v-if="selectedCategoria" type="info" variant="tonal" density="compact" class="mb-4">
            Categoría: <strong>{{ selectedCategoria.nombre }}</strong>
          </v-alert>
          <v-form ref="productoFormRef">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="productoForm.codigo" label="Código" :rules="[requiredRule]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="productoForm.nombre" label="Nombre" :rules="[requiredRule]" />
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="productoForm.descripcion" label="Descripción" rows="2" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="productoForm.marca_id"
                  :items="marcas"
                  item-title="nombre"
                  item-value="id"
                  label="Marca (opcional)"
                  clearable
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="productoForm.unidad_medida_id"
                  :items="unidades"
                  item-title="nombre"
                  item-value="id"
                  label="Unidad de medida"
                  :rules="[requiredRule]"
                />
              </v-col>
              <v-col cols="12" sm="6" class="d-flex align-center">
                <v-switch v-model="productoForm.activo" label="Activo" color="success" hide-details inset />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-5 pt-0">
          <v-spacer />
          <v-btn variant="text" @click="productoDialog = false">Cancelar</v-btn>
          <v-btn color="primary" variant="flat" :loading="savingProducto" @click="saveProducto">Guardar</v-btn>
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

.detail-table-area {
  min-height: 280px;
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

.detail-panel__header {
  background: rgb(var(--v-theme-surface));
}

.detail-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 12px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.detail-empty,
.empty-master {
  color: rgba(var(--v-theme-on-surface), 0.7);
}

@media (max-width: 960px) {
  .master-panel {
    border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    max-height: 320px;
    overflow-y: auto;
  }

  .detail-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .detail-toolbar .v-btn {
    width: 100%;
  }
}
</style>
