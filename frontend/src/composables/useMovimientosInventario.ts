import { computed, ref, unref, type MaybeRef } from 'vue'
import { catalogosService } from '@/services/catalogos.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import {
  enrichMovimiento,
  filterMovimientos,
  type MovimientoInventarioRow,
} from '@/utils/inventario-movimientos'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen, MovimientoInventario, TipoMovimiento } from '@/types/inventario.types'

export function useMovimientosInventario() {
  const appStore = useAppStore()

  const movimientos = ref<MovimientoInventario[]>([])
  const productos = ref<Producto[]>([])
  const almacenes = ref<Almacen[]>([])
  const loading = ref(false)
  const catalogosReady = ref(false)

  const productoMap = computed(() =>
    Object.fromEntries(productos.value.map((p) => [p.id, { nombre: p.nombre, codigo: p.codigo }])),
  )
  const productoNombreMap = computed(() =>
    Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])),
  )
  const almacenMap = computed(() => Object.fromEntries(almacenes.value.map((a) => [a.id, a.nombre])))

  const tableRows = computed<MovimientoInventarioRow[]>(() =>
    movimientos.value.map((m) => enrichMovimiento(m, productoMap.value, almacenMap.value)),
  )

  function filteredRows(filters: {
    productoId?: MaybeRef<number | null | undefined>
    almacenId?: MaybeRef<number | null | undefined>
    tipos?: MaybeRef<TipoMovimiento[] | undefined>
    referenciaTipo?: MaybeRef<string | null | undefined>
    referenciaId?: MaybeRef<number | null | undefined>
  }) {
    return computed(() =>
      filterMovimientos(movimientos.value, {
        productoId: unref(filters.productoId),
        almacenId: unref(filters.almacenId),
        tipos: unref(filters.tipos),
        referenciaTipo: unref(filters.referenciaTipo),
        referenciaId: unref(filters.referenciaId),
      }).map((m) => enrichMovimiento(m, productoMap.value, almacenMap.value)),
    )
  }

  async function loadCatalogos() {
    const [productosRes, almacenesRes] = await Promise.all([
      catalogosService.getProductos(),
      inventarioService.getAlmacenes(),
    ])
    productos.value = productosRes.data
    almacenes.value = almacenesRes.data.filter((a) => a.activo)
    catalogosReady.value = true
  }

  async function loadMovimientos() {
    loading.value = true
    try {
      const { data } = await inventarioService.getMovimientos({ limit: 500 })
      movimientos.value = data
    } catch (error) {
      appStore.showError(getErrorMessage(error))
    } finally {
      loading.value = false
    }
  }

  async function refresh() {
    try {
      if (!catalogosReady.value) await loadCatalogos()
      await loadMovimientos()
    } catch (error) {
      appStore.showError(getErrorMessage(error))
    }
  }

  return {
    movimientos,
    productos,
    almacenes,
    loading,
    catalogosReady,
    productoMap,
    productoNombreMap,
    almacenMap,
    tableRows,
    filteredRows,
    loadCatalogos,
    loadMovimientos,
    refresh,
  }
}
