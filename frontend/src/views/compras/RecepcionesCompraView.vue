<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import BaseDataTable from '@/components/BaseDataTable.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { catalogosService } from '@/services/catalogos.service'
import { comprasService } from '@/services/compras.service'
import { inventarioService } from '@/services/inventario.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import MovimientosInventarioTable from '@/components/MovimientosInventarioTable.vue'
import { enrichMovimiento } from '@/utils/inventario-movimientos'
import { formatInteger, formatMoney } from '@/utils/format'
import { positiveIntegerRule, requiredRule } from '@/utils/validation'
import type { Producto } from '@/types/catalogos.types'
import type { Almacen, MovimientoInventario } from '@/types/inventario.types'
import {
  ESTADO_COMPRA_COLORS,
  type OrdenCompra,
  type RecepcionCompra,
  type RecepcionCompraCreate,
} from '@/types/compras.types'

interface DetalleRow {
  key: number
  producto_id: number | null
  cantidad_recibida: number | null
  costo_unitario: number | null
  cantidad_pendiente: number
  cantidad_ordenada: number
  cantidad_ya_recibida: number
  precio_orden: number
  incluido: boolean
}

const appStore = useAppStore()
const items = ref<RecepcionCompra[]>([])
const ordenes = ref<OrdenCompra[]>([])
const almacenes = ref<Almacen[]>([])
const productos = ref<Producto[]>([])
const loading = ref(false)
const search = ref('')
const filterOrden = ref<number | null>(null)
const filterEstado = ref<'all' | 'BORRADOR' | 'CONFIRMADA' | 'CANCELADA'>('all')
const dialog = ref(false)
const detailDialog = ref(false)
const confirmOpen = ref(false)
const confirmAction = ref<'delete' | 'cancel' | 'confirm' | null>(null)
const saving = ref(false)
const acting = ref(false)
const actingId = ref<number | null>(null)
const editingId = ref<number | null>(null)
const editingOrdenId = ref<number | null>(null)
const actionTarget = ref<RecepcionCompra | null>(null)
const detailItem = ref<RecepcionCompra | null>(null)
const detailMovimientos = ref<MovimientoInventario[]>([])
const loadingMovimientos = ref(false)
const movimientosCache = ref<MovimientoInventario[]>([])
const nextRowKey = ref(1)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = reactive({
  almacen_id: null as number | null,
  fecha: new Date().toISOString().slice(0, 10),
  observacion: '',
})
const detalles = ref<DetalleRow[]>([
  {
    key: 0,
    producto_id: null,
    cantidad_recibida: null,
    costo_unitario: null,
    cantidad_pendiente: 0,
    cantidad_ordenada: 0,
    cantidad_ya_recibida: 0,
    precio_orden: 0,
    incluido: true,
  },
])

function getOrdenCompraId(r: RecepcionCompra & { orden_id?: number }): number {
  return r.orden_compra_id ?? r.orden_id ?? 0
}

const ordenesDisponibles = computed(() => {
  const idsConRecepcion = new Set(items.value.map(getOrdenCompraId).filter(Boolean))
  return ordenes.value.filter((o) => o.estado === 'APROBADA' || idsConRecepcion.has(o.id))
})

const ordenesAprobadas = computed(() => ordenes.value.filter((o) => o.estado === 'APROBADA'))

const ordenesConPendiente = computed(() =>
  ordenesAprobadas.value.filter((o) => productosPendientesOrden(o.id).length > 0),
)

const ordenProgreso = computed(() => {
  if (!filterOrden.value || !ordenResumen.value.length) return null
  const total = ordenResumen.value.length
  const completos = ordenResumen.value.filter((r) => r.pendiente === 0).length
  return {
    total,
    completos,
    pendientes: total - completos,
    pct: total ? Math.round((completos / total) * 100) : 0,
  }
})

const lineasIncluidas = computed(() => detalles.value.filter((d) => d.incluido && d.producto_id))

const totalRecepcionIncluida = computed(() =>
  lineasIncluidas.value.reduce((acc, d) => {
    if (!d.cantidad_recibida || d.costo_unitario === null) return acc
    return acc + Number(d.cantidad_recibida) * Number(d.costo_unitario)
  }, 0),
)

const ordenMap = computed(() => Object.fromEntries(ordenes.value.map((o) => [o.id, o.codigo])))
const productoMap = computed(() => Object.fromEntries(productos.value.map((p) => [p.id, p.nombre])))
const almacenNombreMap = computed(() => Object.fromEntries(almacenes.value.map((a) => [a.id, a.nombre])))

const detailMovimientosRows = computed(() =>
  detailMovimientos.value.map((m) =>
    enrichMovimiento(m, productoMap.value, almacenNombreMap.value),
  ),
)

const dialogOrdenId = computed(() => editingOrdenId.value)

const ordenSeleccionada = computed(() =>
  ordenes.value.find((o) => o.id === dialogOrdenId.value) ?? null,
)

const ordenItems = computed(() => {
  if (!filterOrden.value) return items.value
  return items.value.filter((r) => getOrdenCompraId(r) === filterOrden.value)
})

const stats = computed(() => {
  const base = ordenItems.value
  const borradores = base.filter((r) => r.estado === 'BORRADOR').length
  const confirmadas = base.filter((r) => r.estado === 'CONFIRMADA').length
  const montoConfirmado = base
    .filter((r) => r.estado === 'CONFIRMADA')
    .reduce((acc, r) => acc + Number(r.total), 0)
  return { total: base.length, borradores, confirmadas, montoConfirmado }
})

const hasFilters = computed(() => filterOrden.value != null || filterEstado.value !== 'all')

const tableItems = computed(() => {
  let result = ordenItems.value
  if (filterEstado.value !== 'all') {
    result = result.filter((r) => r.estado === filterEstado.value)
  }
  return result.map((r) => ({
    ...r,
    orden_codigo: ordenMap.value[getOrdenCompraId(r)] ?? '',
  }))
})

const ordenTienePendiente = computed(() => {
  if (!filterOrden.value) return false
  return ordenResumen.value.some((r) => r.pendiente > 0)
})

const ordenResumen = computed(() => {
  if (!filterOrden.value) return []
  const orden = ordenes.value.find((o) => o.id === filterOrden.value)
  if (!orden) return []
  return orden.detalles.map((d) => {
    const ordenada = Math.floor(getCantidadOrdenada(filterOrden.value!, d.producto_id))
    const confirmada = Math.floor(cantidadRecibidaConfirmada(filterOrden.value!, d.producto_id, null))
    const enBorradores = Math.floor(cantidadEnBorradores(filterOrden.value!, d.producto_id, null))
    const recibida = confirmada + enBorradores
    const pendiente = Math.max(0, ordenada - recibida)
    const prod = productos.value.find((p) => p.id === d.producto_id)
    return {
      producto_id: d.producto_id,
      nombre: prod?.nombre ?? d.producto_nombre ?? `Producto ${d.producto_id}`,
      ordenada,
      recibida,
      pendiente,
      precio: Number(d.precio_unitario),
    }
  })
})

const estadoOptions = [
  { value: 'all', title: 'Todos' },
  { value: 'BORRADOR', title: 'Borrador' },
  { value: 'CONFIRMADA', title: 'Confirmada' },
  { value: 'CANCELADA', title: 'Cancelada' },
]

const confirmDialogConfig = computed(() => {
  const codigo = actionTarget.value?.codigo ?? ''
  if (confirmAction.value === 'confirm') {
    return {
      title: 'Confirmar recepción',
      message: `¿Confirmar la recepción ${codigo}? Se registrará el ingreso de mercancía en inventario.`,
      confirmText: 'Sí, confirmar',
      confirmColor: 'success',
      icon: 'mdi-check-circle-outline',
      iconColor: 'success',
    }
  }
  if (confirmAction.value === 'cancel') {
    return {
      title: 'Cancelar recepción',
      message: `¿Cancelar la recepción ${codigo}? No se modificará el inventario.`,
      confirmText: 'Sí, cancelar',
      confirmColor: 'warning',
      icon: 'mdi-cancel',
      iconColor: 'warning',
    }
  }
  return {
    title: 'Eliminar recepción',
    message: `¿Eliminar la recepción ${codigo}? Solo aplica a borradores y no se puede deshacer.`,
    confirmText: 'Sí, eliminar',
    confirmColor: 'error',
    icon: 'mdi-delete-outline',
    iconColor: 'error',
  }
})


const headers = computed(() => [
  { title: 'Número', key: 'codigo', width: 108 },
  ...(filterOrden.value
    ? []
    : [{ title: 'Orden', key: 'orden_compra_id', width: 100, sortable: false }]),
  { title: 'Almacén', key: 'almacen_nombre', width: 140 },
  { title: 'Fecha', key: 'fecha', width: 96 },
  { title: 'Estado', key: 'estado', width: 96, sortable: false },
  { title: 'Total', key: 'total', align: 'end' as const, width: 108 },
  { title: '', key: 'actions', sortable: false, align: 'end' as const, width: 72 },
])

function formatFecha(value?: string | null) {
  if (!value) return '—'
  const [y, m, d] = value.slice(0, 10).split('-')
  if (!y || !m || !d) return value
  return `${d}/${m}/${y}`
}

function cantidadRecibidaConfirmada(
  ordenId: number,
  productoId: number,
  excludeRecepcionId?: number | null,
): number {
  return items.value
    .filter(
      (r) =>
        getOrdenCompraId(r) === ordenId &&
        r.estado === 'CONFIRMADA' &&
        r.id !== excludeRecepcionId,
    )
    .flatMap((r) => r.detalles)
    .filter((d) => d.producto_id === productoId)
    .reduce((sum, d) => sum + Number(d.cantidad_recibida), 0)
}

function cantidadEnBorradores(
  ordenId: number,
  productoId: number,
  excludeRecepcionId?: number | null,
): number {
  return items.value
    .filter(
      (r) =>
        getOrdenCompraId(r) === ordenId &&
        r.estado === 'BORRADOR' &&
        r.id !== excludeRecepcionId,
    )
    .flatMap((r) => r.detalles)
    .filter((d) => d.producto_id === productoId)
    .reduce((sum, d) => sum + Number(d.cantidad_recibida), 0)
}

function getPrecioOrden(ordenId: number, productoId: number): number {
  const orden = ordenes.value.find((o) => o.id === ordenId)
  const det = orden?.detalles.find((d) => d.producto_id === productoId)
  return det ? Number(det.precio_unitario) : 0
}

function getCantidadOrdenada(ordenId: number, productoId: number): number {
  const orden = ordenes.value.find((o) => o.id === ordenId)
  const det = orden?.detalles.find((d) => d.producto_id === productoId)
  return det ? Number(det.cantidad) : 0
}

function getPendienteProducto(
  ordenId: number,
  productoId: number,
  excludeRecepcionId?: number | null,
): number {
  const ordenada = getCantidadOrdenada(ordenId, productoId)
  const confirmada = cantidadRecibidaConfirmada(ordenId, productoId, excludeRecepcionId)
  const enBorradores = cantidadEnBorradores(ordenId, productoId, excludeRecepcionId)
  return Math.max(0, Math.floor(ordenada - confirmada - enBorradores))
}

function buildRowMeta(ordenId: number, productoId: number, excludeRecepcionId?: number | null) {
  const ordenada = Math.floor(getCantidadOrdenada(ordenId, productoId))
  const confirmada = Math.floor(cantidadRecibidaConfirmada(ordenId, productoId, excludeRecepcionId))
  const enBorradores = Math.floor(cantidadEnBorradores(ordenId, productoId, excludeRecepcionId))
  const yaRecibida = confirmada + enBorradores
  const pendiente = Math.max(0, ordenada - yaRecibida)
  const precio = getPrecioOrden(ordenId, productoId)
  return {
    cantidad_ordenada: ordenada,
    cantidad_ya_recibida: yaRecibida,
    cantidad_pendiente: pendiente,
    precio_orden: precio,
    costo_unitario: precio,
  }
}

function maxCantidadRule(row: DetalleRow) {
  return (value: unknown) => {
    if (!row.producto_id) return true
    const num = Number(value)
    if (!Number.isInteger(num)) return 'Use solo números enteros'
    if (num > row.cantidad_pendiente) return `Máximo: ${row.cantidad_pendiente}`
    return true
  }
}

function productosPendientesOrden(ordenId: number, excludeRecepcionId?: number | null) {
  const orden = ordenes.value.find((o) => o.id === ordenId)
  if (!orden) return []
  return orden.detalles
    .filter((d) => getPendienteProducto(ordenId, d.producto_id, excludeRecepcionId) > 0)
    .map((d) => {
      const prod = productos.value.find((p) => p.id === d.producto_id)
      return {
        id: d.producto_id,
        nombre: prod?.nombre ?? d.producto_nombre ?? `Producto ${d.producto_id}`,
        pendiente: getPendienteProducto(ordenId, d.producto_id, excludeRecepcionId),
        costo: Number(d.precio_unitario),
        ordenada: Math.floor(Number(d.cantidad)),
        precio: Number(d.precio_unitario),
      }
    })
}

function lineSubtotal(row: DetalleRow) {
  if (!row.cantidad_recibida || row.costo_unitario === null) return 0
  return Number(row.cantidad_recibida) * Number(row.costo_unitario)
}

function emptyDetalleRow(): DetalleRow {
  return {
    key: nextRowKey.value++,
    producto_id: null,
    cantidad_recibida: null,
    costo_unitario: null,
    cantidad_pendiente: 0,
    cantidad_ordenada: 0,
    cantidad_ya_recibida: 0,
    precio_orden: 0,
    incluido: true,
  }
}

function toggleIncluido(row: DetalleRow, value: boolean | null) {
  row.incluido = value ?? false
}

function recibirTodoPendiente() {
  for (const row of detalles.value) {
    if (!row.producto_id) continue
    row.incluido = true
    row.cantidad_recibida = row.cantidad_pendiente > 0 ? row.cantidad_pendiente : null
  }
}

function resetForm() {
  form.almacen_id = null
  form.fecha = new Date().toISOString().slice(0, 10)
  form.observacion = ''
  editingOrdenId.value = null
  detalles.value = [emptyDetalleRow()]
}

function clearFilters() {
  filterOrden.value = null
  filterEstado.value = 'all'
}

async function loadMovimientosRecepcion(recepcionId: number) {
  loadingMovimientos.value = true
  try {
    if (!movimientosCache.value.length) {
      const { data } = await inventarioService.getMovimientos()
      movimientosCache.value = data
    }
    detailMovimientos.value = movimientosCache.value.filter(
      (m) => m.referencia_tipo === 'RECEPCION_COMPRA' && m.referencia_id === recepcionId,
    )
  } catch {
    detailMovimientos.value = []
  } finally {
    loadingMovimientos.value = false
  }
}

function loadDetallesFromOrden(ordenId: number | null, excludeRecepcionId?: number | null) {
  if (!ordenId) return
  const pendientes = productosPendientesOrden(ordenId, excludeRecepcionId)
  if (!pendientes.length) {
    detalles.value = [emptyDetalleRow()]
    return
  }
  detalles.value = pendientes.map((p) => {
    const meta = buildRowMeta(ordenId, p.id, excludeRecepcionId)
    return {
      key: nextRowKey.value++,
      producto_id: p.id,
      cantidad_recibida: meta.cantidad_pendiente,
      costo_unitario: meta.costo_unitario,
      cantidad_pendiente: meta.cantidad_pendiente,
      cantidad_ordenada: meta.cantidad_ordenada,
      cantidad_ya_recibida: meta.cantidad_ya_recibida,
      precio_orden: meta.precio_orden,
      incluido: true,
    }
  })
}

function onCantidadInput(row: DetalleRow, value: string | number) {
  if (value === '' || value == null) {
    row.cantidad_recibida = null
    return
  }
  const entero = Math.floor(Number(value))
  row.cantidad_recibida = entero > 0 ? entero : null
}

function validateDetalles(): boolean {
  const ordenId = dialogOrdenId.value
  if (!ordenId) {
    appStore.showError('Seleccione una orden de compra')
    return false
  }
  const lineas = detalles.value.filter((d) => d.incluido && d.producto_id)
  if (!lineas.length) {
    appStore.showError('Seleccione al menos un producto para recibir')
    return false
  }
  for (const d of lineas) {
    if (d.cantidad_recibida == null || d.costo_unitario == null) {
      appStore.showError('Complete cantidad y costo en todas las líneas')
      return false
    }
    if (!Number.isInteger(Number(d.cantidad_recibida)) || Number(d.cantidad_recibida) <= 0) {
      appStore.showError('La cantidad recibida debe ser un entero mayor a 0')
      return false
    }
    if (Number(d.costo_unitario) < 0) {
      appStore.showError('El costo no puede ser negativo')
      return false
    }
    const pendiente = getPendienteProducto(ordenId, d.producto_id!, editingId.value)
    if (Number(d.cantidad_recibida) > pendiente) {
      const nombre = productoMap.value[d.producto_id!] ?? d.producto_id
      appStore.showError(
        `${nombre}: cantidad excede lo pendiente (${pendiente} disponible, ya recibido en otras recepciones)`,
      )
      return false
    }
  }
  const ids = lineas.map((d) => d.producto_id)
  if (new Set(ids).size !== ids.length) {
    appStore.showError('No repita el mismo producto en varias líneas')
    return false
  }
  return true
}

watch(dialogOrdenId, (id) => {
  if (!editingId.value && dialog.value && id) loadDetallesFromOrden(id)
})

async function loadData() {
  loading.value = true
  try {
    const [recRes, ordRes, almRes, prodRes] = await Promise.all([
      comprasService.getRecepcionesCompra(),
      comprasService.getOrdenesCompra(),
      inventarioService.getAlmacenes(),
      catalogosService.getProductos(),
    ])
    items.value = recRes.data
    ordenes.value = ordRes.data
    almacenes.value = almRes.data.filter((a) => a.activo)
    productos.value = prodRes.data.filter((p) => p.activo)
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  resetForm()
  editingOrdenId.value = filterOrden.value ?? ordenesConPendiente.value[0]?.id ?? null
  if (editingOrdenId.value) loadDetallesFromOrden(editingOrdenId.value)
  if (almacenes.value.length === 1) form.almacen_id = almacenes.value[0]!.id
  dialog.value = true
}

function openEdit(item: RecepcionCompra) {
  if (item.estado !== 'BORRADOR') {
    appStore.showError('Solo se pueden editar recepciones en BORRADOR')
    return
  }
  editingId.value = item.id
  editingOrdenId.value = getOrdenCompraId(item)
  form.almacen_id = item.almacen_id
  form.fecha = item.fecha ?? new Date().toISOString().slice(0, 10)
  form.observacion = item.observacion ?? ''
  detalles.value = item.detalles.map((d) => {
    const cantidad = Math.floor(Number(d.cantidad_recibida))
    const meta = buildRowMeta(getOrdenCompraId(item), d.producto_id, item.id)
    return {
      ...meta,
      key: nextRowKey.value++,
      producto_id: d.producto_id,
      cantidad_recibida: cantidad,
      costo_unitario: Number(d.costo_unitario),
      incluido: true,
    }
  })
  dialog.value = true
}

async function openDetail(item: RecepcionCompra) {
  detailItem.value = item
  detailMovimientos.value = []
  detailDialog.value = true
  if (item.estado === 'CONFIRMADA') {
    await loadMovimientosRecepcion(item.id)
  }
}

function openConfirm(item: RecepcionCompra) {
  actionTarget.value = item
  confirmAction.value = 'confirm'
  confirmOpen.value = true
}

function openCancel(item: RecepcionCompra) {
  actionTarget.value = item
  confirmAction.value = 'cancel'
  confirmOpen.value = true
}

function openDelete(item: RecepcionCompra) {
  actionTarget.value = item
  confirmAction.value = 'delete'
  confirmOpen.value = true
}

async function saveItem(confirmAfterSave = false) {
  const validation = await formRef.value?.validate()
  if (!validation?.valid || !dialogOrdenId.value || !form.almacen_id) return
  if (!validateDetalles()) return

  const lineas = detalles.value.filter(
    (d) =>
      d.incluido &&
      d.producto_id &&
      d.cantidad_recibida != null &&
      d.costo_unitario != null &&
      Number(d.cantidad_recibida) > 0 &&
      Number.isInteger(Number(d.cantidad_recibida)) &&
      Number(d.costo_unitario) >= 0,
  )

  const payload: RecepcionCompraCreate = {
    orden_compra_id: dialogOrdenId.value,
    almacen_id: form.almacen_id,
    fecha: form.fecha,
    observacion: form.observacion || null,
    detalles: lineas.map((d) => ({
      producto_id: d.producto_id!,
      cantidad_recibida: Math.floor(Number(d.cantidad_recibida)),
      costo_unitario: d.costo_unitario!,
    })),
  }

  saving.value = true
  try {
    let recepcionId = editingId.value
    if (editingId.value) {
      const { data } = await comprasService.updateRecepcionCompra(editingId.value, payload)
      if (confirmAfterSave) {
        recepcionId = data.id
      } else {
        appStore.showSuccess(`Recepción ${data.codigo} actualizada`)
      }
    } else {
      const { data } = await comprasService.createRecepcionCompra(payload)
      recepcionId = data.id
      if (!confirmAfterSave) {
        appStore.showSuccess(`Recepción ${data.codigo} creada`)
      }
    }

    if (confirmAfterSave && recepcionId) {
      const { data } = await comprasService.confirmarRecepcionCompra(recepcionId)
      movimientosCache.value = []
      appStore.showSuccess(`Recepción ${data.codigo} confirmada — ingreso registrado en inventario`)
    }

    dialog.value = false
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

async function confirmActionHandler() {
  if (!actionTarget.value || !confirmAction.value) return
  actingId.value = actionTarget.value.id
  acting.value = true
  try {
    if (confirmAction.value === 'confirm') {
      const { data } = await comprasService.confirmarRecepcionCompra(actionTarget.value.id)
      movimientosCache.value = []
      appStore.showSuccess(`Recepción ${data.codigo} confirmada — ingreso registrado en inventario`)
    } else if (confirmAction.value === 'cancel') {
      await comprasService.cancelarRecepcionCompra(actionTarget.value.id)
      appStore.showSuccess('Recepción cancelada')
    } else {
      await comprasService.deleteRecepcionCompra(actionTarget.value.id)
      appStore.showSuccess('Recepción eliminada')
    }
    confirmOpen.value = false
    actionTarget.value = null
    confirmAction.value = null
    await loadData()
  } catch (error) {
    appStore.showError(getErrorMessage(error))
  } finally {
    acting.value = false
    actingId.value = null
  }
}

onMounted(loadData)
</script>

<template>
  <div class="recepciones-page">
    <PageHeader
      title="Recepciones de Compra"
      subtitle="Registra la mercancía recibida y actualiza el inventario"
      icon="mdi-package-down"
    >
      <template #actions>
        <v-btn
          variant="tonal"
          size="small"
          prepend-icon="mdi-refresh"
          :loading="loading"
          @click="loadData"
        >
          Actualizar
        </v-btn>
        <v-btn
          color="primary"
          size="small"
          prepend-icon="mdi-plus"
          @click="openCreate"
        >
          Nueva recepción
        </v-btn>
      </template>
    </PageHeader>

    <div class="toolbar">
      <v-select
        v-model="filterOrden"
        :items="ordenesDisponibles"
        item-title="codigo"
        item-value="id"
        label="Orden de compra"
        hide-details
        clearable
        density="compact"
        prepend-inner-icon="mdi-file-document-outline"
        placeholder="Todas las órdenes"
        class="toolbar__orden"
      />
      <v-select
        v-model="filterEstado"
        :items="estadoOptions"
        item-title="title"
        item-value="value"
        label="Estado"
        hide-details
        density="compact"
        prepend-inner-icon="mdi-filter-variant"
        class="toolbar__estado"
      />
      <v-btn
        v-if="hasFilters"
        size="small"
        variant="text"
        prepend-icon="mdi-filter-off-outline"
        @click="clearFilters"
      >
        Limpiar
      </v-btn>
      <div class="toolbar__stats">
        <span class="toolbar__stat">{{ stats.total }} recep.</span>
        <span v-if="stats.borradores" class="toolbar__stat toolbar__stat--warn">{{ stats.borradores }} borrador</span>
        <span class="toolbar__stat toolbar__stat--ok">{{ stats.confirmadas }} confirmada</span>
      </div>
    </div>

    <v-card
      v-if="filterOrden && ordenProgreso && ordenTienePendiente"
      class="quick-receive"
      variant="outlined"
    >
      <div class="quick-receive__body">
        <div class="quick-receive__info">
          <div class="quick-receive__title">
            Orden {{ ordenMap[filterOrden] }}
          </div>
          <p class="quick-receive__desc">
            {{ ordenProgreso.pendientes }} producto{{ ordenProgreso.pendientes === 1 ? '' : 's' }} pendiente{{ ordenProgreso.pendientes === 1 ? '' : 's' }} de recibir
          </p>
          <v-progress-linear
            :model-value="ordenProgreso.pct"
            color="success"
            height="6"
            rounded
            class="quick-receive__progress"
          />
          <span class="quick-receive__progress-label">
            {{ ordenProgreso.completos }}/{{ ordenProgreso.total }} productos completos
          </span>
        </div>
        <v-btn
          color="primary"
          prepend-icon="mdi-package-down"
          @click="openCreate"
        >
          Recibir mercancía
        </v-btn>
      </div>
    </v-card>

    <v-alert
      v-else-if="filterOrden && !ordenTienePendiente"
      type="success"
      variant="tonal"
      density="compact"
      icon="mdi-check-all"
    >
      Orden {{ ordenMap[filterOrden] }} — recibida por completo.
    </v-alert>

    <v-alert
      v-else-if="ordenesConPendiente.length"
      type="info"
      variant="tonal"
      density="compact"
      icon="mdi-information-outline"
    >
      Elija una orden con productos pendientes o pulse «Nueva recepción» para comenzar.
    </v-alert>

      <BaseDataTable
        v-model:search="search"
        :items="tableItems as Record<string, unknown>[]"
        :headers="headers"
        :loading="loading"
        title="Listado"
        :subtitle="filterOrden ? `Recepciones de orden ${ordenMap[filterOrden] ?? ''}` : 'Todas las recepciones de compra'"
        search-label="Buscar número, orden o almacén..."
        empty-icon="mdi-package-variant-closed-remove"
        empty-title="Sin recepciones"
        empty-subtitle="Registra la primera recepción para ingresar mercancía al inventario."
      >
        <template #item.codigo="{ value }">
          <span class="code-badge">{{ value }}</span>
        </template>

        <template #item.orden_compra_id="{ item }">
          <span class="code-badge code-badge--muted">
            {{ ordenMap[getOrdenCompraId(item as RecepcionCompra)] ?? getOrdenCompraId(item as RecepcionCompra) }}
          </span>
        </template>

        <template #item.almacen_nombre="{ item }">
          <span class="cell-ellipsis" :title="item.almacen_nombre ?? String(item.almacen_id)">
            <v-icon icon="mdi-warehouse" size="12" class="mr-1 text-medium-emphasis" />
            {{ item.almacen_nombre ?? item.almacen_id }}
          </span>
        </template>

        <template #item.fecha="{ value }">
          <span class="text-caption">{{ formatFecha(value) }}</span>
        </template>

        <template #item.total="{ value }">
          <span class="money-cell">{{ formatMoney(value) }}</span>
        </template>

        <template #item.estado="{ value }">
          <v-chip :color="ESTADO_COMPRA_COLORS[value] ?? 'default'" size="x-small" variant="tonal" label>
            {{ value }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <div class="row-actions">
            <v-btn
              v-if="item.estado === 'BORRADOR'"
              icon="mdi-check-circle-outline"
              size="x-small"
              variant="text"
              color="success"
              aria-label="Confirmar"
              :loading="acting && actingId === item.id"
              @click="openConfirm(item as RecepcionCompra)"
            />
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
                  prepend-icon="mdi-eye-outline"
                  title="Ver detalle"
                  @click="openDetail(item as RecepcionCompra)"
                />
                <v-list-item
                  v-if="item.estado === 'BORRADOR'"
                  prepend-icon="mdi-pencil-outline"
                  title="Editar"
                  @click="openEdit(item as RecepcionCompra)"
                />
                <v-list-item
                  v-if="item.estado === 'BORRADOR'"
                  prepend-icon="mdi-cancel"
                  title="Cancelar"
                  base-color="warning"
                  @click="openCancel(item as RecepcionCompra)"
                />
                <v-list-item
                  v-if="item.estado === 'BORRADOR'"
                  prepend-icon="mdi-delete-outline"
                  title="Eliminar"
                  base-color="error"
                  @click="openDelete(item as RecepcionCompra)"
                />
              </v-list>
            </v-menu>
          </div>
        </template>
      </BaseDataTable>
  </div>

  <v-dialog v-model="dialog" max-width="720" persistent scrollable>
    <v-card border elevation="0">
      <v-card-title class="dialog-title pa-4 pb-2">
        <v-avatar color="primary" variant="tonal" size="36" rounded="md">
          <v-icon :icon="editingId ? 'mdi-pencil-outline' : 'mdi-package-down'" size="18" />
        </v-avatar>
        <span>{{ editingId ? 'Editar recepción' : 'Recibir mercancía' }}</span>
      </v-card-title>

      <v-card-text class="pa-4 pt-2">
        <v-form ref="formRef">
          <v-select
            v-if="!editingId && !filterOrden"
            v-model="editingOrdenId"
            :items="ordenesConPendiente"
            item-title="codigo"
            item-value="id"
            label="Orden de compra *"
            density="compact"
            prepend-inner-icon="mdi-file-document-outline"
            class="mb-3"
            :rules="[requiredRule]"
          />

          <div v-if="ordenSeleccionada" class="form-orden mb-3">
            <v-icon icon="mdi-file-document-outline" size="16" class="form-orden__icon" />
            <span class="form-orden__label">Orden</span>
            <span class="form-orden__name">{{ ordenSeleccionada.codigo }}</span>
          </div>

          <v-row dense>
            <v-col cols="12" sm="7">
              <v-select
                v-model="form.almacen_id"
                :items="almacenes"
                item-title="nombre"
                item-value="id"
                label="Almacén destino *"
                density="compact"
                prepend-inner-icon="mdi-warehouse"
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col cols="12" sm="5">
              <v-text-field
                v-model="form.fecha"
                label="Fecha *"
                type="date"
                density="compact"
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.observacion"
                label="Observación (opcional)"
                density="compact"
                hide-details
                prepend-inner-icon="mdi-note-text-outline"
              />
            </v-col>
          </v-row>

          <div class="receive-section">
            <div class="receive-section__header">
              <span class="receive-section__title">Productos a recibir</span>
              <v-btn
                size="x-small"
                variant="text"
                prepend-icon="mdi-check-all"
                :disabled="!dialogOrdenId"
                @click="recibirTodoPendiente"
              >
                Marcar todo
              </v-btn>
            </div>

            <v-alert
              v-if="dialogOrdenId && !productosPendientesOrden(dialogOrdenId, editingId).length && !editingId"
              type="warning"
              variant="tonal"
              density="compact"
              class="mb-2"
            >
              Todos los productos de esta orden ya fueron recibidos.
            </v-alert>

            <div v-else class="receive-list">
              <div
                v-for="row in detalles.filter((d) => d.producto_id)"
                :key="row.key"
                class="receive-item"
                :class="{ 'receive-item--off': !row.incluido }"
              >
                <v-checkbox
                  :model-value="row.incluido"
                  density="compact"
                  hide-details
                  class="receive-item__check"
                  @update:model-value="toggleIncluido(row, $event)"
                />
                <div class="receive-item__info">
                  <span class="receive-item__name">
                    {{ productoMap[row.producto_id!] ?? row.producto_id }}
                  </span>
                  <span class="receive-item__meta">
                    Pendiente: {{ formatInteger(row.cantidad_pendiente) }}
                    · Precio: {{ formatMoney(row.precio_orden) }}
                  </span>
                </div>
                <v-text-field
                  :model-value="row.cantidad_recibida"
                  label="Cantidad"
                  type="number"
                  min="1"
                  :max="row.cantidad_pendiente || undefined"
                  step="1"
                  density="compact"
                  hide-details
                  class="receive-item__qty"
                  :disabled="!row.incluido"
                  :rules="row.incluido ? [requiredRule, positiveIntegerRule, maxCantidadRule(row)] : []"
                  @update:model-value="onCantidadInput(row, $event)"
                />
                <span class="receive-item__sub">
                  {{ formatMoney(lineSubtotal(row)) }}
                </span>
              </div>
            </div>

            <div class="receive-total">
              <span>{{ lineasIncluidas.length }} producto{{ lineasIncluidas.length === 1 ? '' : 's' }} seleccionado{{ lineasIncluidas.length === 1 ? '' : 's' }}</span>
              <strong>{{ formatMoney(totalRecepcionIncluida) }}</strong>
            </div>
          </div>
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4 pt-0">
        <v-spacer />
        <v-btn variant="text" size="small" @click="dialog = false">Cancelar</v-btn>
        <v-btn
          variant="tonal"
          size="small"
          :loading="saving"
          :disabled="!lineasIncluidas.length"
          @click="saveItem(false)"
        >
          Guardar borrador
        </v-btn>
        <v-btn
          color="success"
          size="small"
          variant="flat"
          prepend-icon="mdi-check-circle-outline"
          :loading="saving"
          :disabled="!lineasIncluidas.length"
          @click="saveItem(true)"
        >
          Recibir ahora
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="detailDialog" max-width="640">
    <v-card v-if="detailItem" border elevation="0">
      <v-card-title class="dialog-title pa-4 pb-2">
        <v-avatar color="primary" variant="tonal" size="36" rounded="md">
          <v-icon icon="mdi-package-down" size="18" />
        </v-avatar>
        <div class="dialog-title__text">
          <span>Recepción {{ detailItem.codigo }}</span>
          <v-chip
            :color="ESTADO_COMPRA_COLORS[detailItem.estado] ?? 'default'"
            size="x-small"
            variant="tonal"
            label
            class="mt-1"
          >
            {{ detailItem.estado }}
          </v-chip>
        </div>
      </v-card-title>

      <v-card-text class="pa-4 pt-2">
        <div class="detail-meta">
          <div class="detail-meta__item">
            <v-icon icon="mdi-file-document-outline" size="14" class="detail-meta__icon" />
            <span>{{ ordenMap[getOrdenCompraId(detailItem)] }}</span>
          </div>
          <div class="detail-meta__item">
            <v-icon icon="mdi-warehouse" size="14" class="detail-meta__icon" />
            <span>{{ detailItem.almacen_nombre }}</span>
          </div>
          <div class="detail-meta__item">
            <v-icon icon="mdi-calendar-outline" size="14" class="detail-meta__icon" />
            <span>{{ formatFecha(detailItem.fecha) }}</span>
          </div>
          <div class="detail-meta__item detail-meta__item--total">
            <span>Total</span>
            <strong>{{ formatMoney(detailItem.total) }}</strong>
          </div>
        </div>

        <v-table density="compact" class="detail-table mt-3">
          <thead>
            <tr>
              <th>Producto</th>
              <th class="text-end">Cant.</th>
              <th class="text-end">Precio</th>
              <th class="text-end">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in detailItem.detalles" :key="d.id">
              <td class="detail-table__product">
                {{ d.producto_nombre ?? productoMap[d.producto_id] ?? d.producto_id }}
              </td>
              <td class="text-end">{{ formatInteger(d.cantidad_recibida) }}</td>
              <td class="text-end">{{ formatMoney(d.costo_unitario) }}</td>
              <td class="text-end font-weight-medium">
                {{ formatMoney(d.subtotal ?? Number(d.cantidad_recibida) * Number(d.costo_unitario)) }}
              </td>
            </tr>
          </tbody>
        </v-table>

        <p v-if="detailItem.observacion" class="detail-obs mt-3">
          <v-icon icon="mdi-note-text-outline" size="14" class="mr-1" />
          {{ detailItem.observacion }}
        </p>

        <v-alert
          v-if="detailItem.estado === 'CONFIRMADA'"
          type="success"
          variant="tonal"
          density="compact"
          class="mt-3"
        >
          Stock ingresado en {{ detailItem.almacen_nombre }}.
        </v-alert>
        <v-alert
          v-else-if="detailItem.estado === 'BORRADOR'"
          type="info"
          variant="tonal"
          density="compact"
          class="mt-3"
        >
          Borrador: aún no afecta existencias. Confirme para ingresar al inventario.
        </v-alert>

        <div v-if="detailItem.estado === 'CONFIRMADA'" class="inventario-impact mt-3">
          <MovimientosInventarioTable
            :items="detailMovimientosRows"
            :loading="loadingMovimientos"
            title="Movimientos generados en inventario"
            subtitle="Ingresos registrados al confirmar esta recepción"
            :show-search="false"
            :show-almacen="false"
            compact
            @refresh="loadMovimientosRecepcion(detailItem.id)"
          />
          <div class="inventario-impact__links">
            <v-btn
              :to="{
                name: 'existencias',
                query: {
                  almacen: detailItem.almacen_id,
                  ...(detailItem.detalles[0]?.producto_id
                    ? { producto: detailItem.detalles[0].producto_id }
                    : {}),
                },
              }"
              size="x-small"
              variant="text"
              prepend-icon="mdi-open-in-new"
            >
              Ver existencias
            </v-btn>
            <v-btn
              :to="{ name: 'kardex' }"
              size="x-small"
              variant="text"
              prepend-icon="mdi-open-in-new"
            >
              Ver kardex
            </v-btn>
          </div>
        </div>
      </v-card-text>

      <v-card-actions class="pa-4 pt-0">
        <v-btn
          v-if="detailItem.estado === 'BORRADOR'"
          color="success"
          size="small"
          variant="flat"
          prepend-icon="mdi-check-circle-outline"
          :loading="acting && actingId === detailItem.id"
          @click="openConfirm(detailItem)"
        >
          Confirmar recepción
        </v-btn>
        <v-spacer />
        <v-btn variant="text" size="small" @click="detailDialog = false">Cerrar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <ConfirmDialog
    v-model="confirmOpen"
    :loading="acting"
    v-bind="confirmDialogConfig"
    @confirm="confirmActionHandler"
  />
</template>

<style scoped>
.recepciones-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: #fff;
}

.toolbar__orden {
  flex: 1 1 220px;
  max-width: 320px;
}

.toolbar__estado {
  flex: 0 0 160px;
}

.toolbar__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-left: auto;
}

.toolbar__stat {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.55);
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(var(--v-theme-on-surface), 0.05);
}

.toolbar__stat--warn {
  color: rgb(var(--v-theme-warning));
  background: rgba(var(--v-theme-warning), 0.1);
}

.toolbar__stat--ok {
  color: rgb(var(--v-theme-success));
  background: rgba(var(--v-theme-success), 0.1);
}

.quick-receive {
  border-color: rgba(var(--v-theme-primary), 0.25) !important;
  background: rgba(var(--v-theme-primary), 0.03);
}

.quick-receive__body {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
}

.quick-receive__info {
  flex: 1 1 240px;
  min-width: 0;
}

.quick-receive__title {
  font-size: 0.9375rem;
  font-weight: 600;
}

.quick-receive__desc {
  margin: 4px 0 8px;
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.6);
}

.quick-receive__progress {
  max-width: 280px;
}

.quick-receive__progress-label {
  display: block;
  margin-top: 4px;
  font-size: 0.6875rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 2px;
}

.empty-orden {
  padding: 48px 24px;
}

.empty-orden__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}

.empty-orden__title {
  margin: 8px 0 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.75);
}

.empty-orden__sub {
  margin: 0;
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.5);
  max-width: 320px;
}

.code-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: var(--mac-text-xs);
  font-weight: 600;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  letter-spacing: 0.02em;
  background: rgba(var(--v-theme-on-surface), 0.06);
  color: rgba(var(--v-theme-on-surface), 0.8);
}

.code-badge--muted {
  background: rgba(var(--v-theme-on-surface), 0.04);
  color: rgba(var(--v-theme-on-surface), 0.65);
}

.inventario-impact {
  padding: 10px 12px;
  border: 1px solid rgba(var(--v-theme-success), 0.25);
  border-radius: var(--mac-radius-sm);
  background: rgba(var(--v-theme-success), 0.04);
}

.inventario-impact__title {
  display: flex;
  align-items: center;
  font-size: var(--mac-text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(var(--v-theme-on-surface), 0.65);
}

.inventario-impact__table {
  margin-top: 8px;
  background: #fff;
  border-radius: var(--mac-radius-sm);
}

.inventario-impact__empty {
  margin: 8px 0 0;
}

.inventario-impact__links {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}

.cell-ellipsis {
  display: block;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.money-cell {
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  font-size: 0.8125rem;
}

.dialog-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1rem;
  font-weight: 600;
}

.dialog-title__text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.form-orden {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  padding: 8px 10px;
  border: 1px solid rgba(var(--v-theme-primary), 0.2);
  border-radius: var(--mac-radius-sm);
  background: rgba(var(--v-theme-primary), 0.05);
}

.form-orden__icon {
  flex-shrink: 0;
  opacity: 0.7;
  color: rgb(var(--v-theme-primary));
}

.form-orden__label {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.form-orden__name {
  font-size: 0.8125rem;
  font-weight: 600;
}

.lines-section,
.receive-section {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.lines-section__header,
.receive-section__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.lines-section__title,
.receive-section__title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.7);
}

.receive-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.receive-item {
  display: grid;
  grid-template-columns: 36px 1fr 100px 72px;
  gap: 8px;
  align-items: center;
  padding: 8px 6px;
  border-radius: var(--mac-radius-sm);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  background: #fff;
}

.receive-item--off {
  opacity: 0.5;
}

.receive-item__check {
  margin: 0;
}

.receive-item__info {
  min-width: 0;
}

.receive-item__name {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.receive-item__meta {
  display: block;
  font-size: 0.6875rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  margin-top: 2px;
}

.receive-item__qty {
  max-width: 100px;
}

.receive-item__sub {
  font-size: var(--mac-text-xs);
  font-variant-numeric: tabular-nums;
  text-align: end;
  font-weight: 500;
}

.receive-total {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  font-size: 0.8125rem;
}

.receive-total strong {
  font-size: 0.9375rem;
  font-variant-numeric: tabular-nums;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  padding: 8px 10px;
  border-radius: var(--mac-radius-sm);
  background: rgba(var(--v-theme-on-surface), 0.04);
}

.detail-meta__item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.75);
}

.detail-meta__item--total {
  margin-left: auto;
  gap: 8px;
}

.detail-meta__item--total strong {
  font-size: 0.875rem;
  font-variant-numeric: tabular-nums;
}

.detail-meta__icon {
  opacity: 0.55;
}

.detail-table :deep(th) {
  font-size: var(--mac-text-xs) !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: rgba(var(--v-theme-on-surface), 0.5) !important;
}

.detail-table__product {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8125rem;
}

.detail-obs {
  font-size: var(--mac-text-xs);
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin: 0;
}

@media (max-width: 600px) {
  .filters-bar__field--estado {
    flex: 1 1 100%;
    min-width: 100%;
    max-width: 100%;
  }

  .orden-gate__select {
    max-width: 100%;
  }

  .detail-meta__item--total {
    margin-left: 0;
    width: 100%;
    justify-content: space-between;
  }
}
</style>
