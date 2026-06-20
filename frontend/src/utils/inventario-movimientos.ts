import type { MovimientoInventario, TipoMovimiento } from '@/types/inventario.types'

export interface MovimientoInventarioRow extends MovimientoInventario {
  producto_nombre: string
  producto_codigo: string
  almacen_nombre: string
  referencia_label: string
}

export const TIPO_MOVIMIENTO_CONFIG: Record<TipoMovimiento, { color: string; label: string }> = {
  INGRESO: { color: 'success', label: 'Ingreso' },
  SALIDA: { color: 'error', label: 'Salida' },
  AJUSTE_POSITIVO: { color: 'info', label: 'Ajuste +' },
  AJUSTE_NEGATIVO: { color: 'warning', label: 'Ajuste −' },
  TRANSFERENCIA_SALIDA: { color: 'secondary', label: 'Trans. salida' },
  TRANSFERENCIA_ENTRADA: { color: 'primary', label: 'Trans. entrada' },
}

export const REFERENCIA_TIPO_LABELS: Record<string, string> = {
  RECEPCION_COMPRA: 'Recepción de compra',
  AJUSTE: 'Ajuste de inventario',
  TRANSFERENCIA: 'Transferencia',
  INGRESO: 'Ingreso manual',
  SALIDA: 'Salida manual',
}

export function isMovimientoEntrada(tipo: TipoMovimiento): boolean {
  return tipo === 'INGRESO' || tipo === 'AJUSTE_POSITIVO' || tipo === 'TRANSFERENCIA_ENTRADA'
}

export function formatReferenciaMovimiento(m: MovimientoInventario): string {
  if (m.observaciones?.trim()) return m.observaciones.trim()
  if (m.referencia_tipo) {
    const label = REFERENCIA_TIPO_LABELS[m.referencia_tipo] ?? m.referencia_tipo
    if (m.referencia_id) return `${label} #${m.referencia_id}`
    return label
  }
  return '—'
}

export function enrichMovimiento(
  m: MovimientoInventario,
  productoMap: Record<number, { nombre: string; codigo?: string } | string>,
  almacenMap: Record<number, string>,
): MovimientoInventarioRow {
  const prod = productoMap[m.producto_id]
  const productoNombre = typeof prod === 'string' ? prod : prod?.nombre ?? `Producto ${m.producto_id}`
  const productoCodigo = typeof prod === 'string' ? '' : prod?.codigo ?? ''
  return {
    ...m,
    producto_nombre: productoNombre,
    producto_codigo: productoCodigo,
    almacen_nombre: almacenMap[m.almacen_id] ?? `Almacén ${m.almacen_id}`,
    referencia_label: formatReferenciaMovimiento(m),
  }
}

export function filterMovimientos(
  movimientos: MovimientoInventario[],
  filters: {
    productoId?: number | null
    almacenId?: number | null
    tipos?: TipoMovimiento[]
    referenciaTipo?: string | null
    referenciaId?: number | null
  },
): MovimientoInventario[] {
  return movimientos.filter((m) => {
    if (filters.productoId != null && m.producto_id !== filters.productoId) return false
    if (filters.almacenId != null && m.almacen_id !== filters.almacenId) return false
    if (filters.tipos?.length && !filters.tipos.includes(m.tipo)) return false
    if (filters.referenciaTipo && m.referencia_tipo !== filters.referenciaTipo) return false
    if (filters.referenciaId != null && m.referencia_id !== filters.referenciaId) return false
    return true
  })
}
