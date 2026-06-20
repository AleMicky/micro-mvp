export interface Auditoria {
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface Proveedor extends Auditoria {
  id: number
  codigo: string
  nombre: string
  rfc?: string | null
  email?: string | null
  telefono?: string | null
  direccion?: string | null
}

export type ProveedorCreate = Omit<Proveedor, 'id' | 'creado_en' | 'actualizado_en'>

export interface OrdenCompraDetalle {
  id?: number
  producto_id: number
  producto_codigo?: string | null
  producto_nombre?: string | null
  cantidad: number | string
  precio_unitario: number | string
  subtotal?: number | string
}

export interface OrdenCompra extends Auditoria {
  id: number
  codigo: string
  proveedor_id: number
  cotizacion_id?: number | null
  estado: string
  fecha?: string | null
  observacion?: string | null
  total: number | string
  detalles: OrdenCompraDetalle[]
}

export interface OrdenCompraCreate {
  proveedor_id: number
  cotizacion_id?: number | null
  fecha?: string | null
  observacion?: string | null
  detalles: Omit<OrdenCompraDetalle, 'id' | 'subtotal' | 'producto_codigo' | 'producto_nombre'>[]
}

export interface RecepcionCompraDetalle {
  id?: number
  producto_id: number
  producto_codigo?: string | null
  producto_nombre?: string | null
  cantidad_recibida: number | string
  costo_unitario: number | string
  subtotal?: number | string
}

export interface RecepcionCompra extends Auditoria {
  id: number
  codigo: string
  orden_compra_id: number
  almacen_id: number
  almacen_nombre?: string | null
  sucursal_id?: number | null
  sucursal_nombre?: string | null
  compania_id?: number | null
  compania_nombre?: string | null
  estado: string
  fecha?: string | null
  observacion?: string | null
  total: number | string
  detalles: RecepcionCompraDetalle[]
}

export interface RecepcionCompraCreate {
  orden_compra_id: number
  almacen_id: number
  fecha?: string | null
  observacion?: string | null
  detalles: Omit<RecepcionCompraDetalle, 'id' | 'subtotal' | 'producto_codigo' | 'producto_nombre'>[]
}

/** @deprecated Mantener para cotizaciones existentes */
export interface DetalleCompra {
  id?: number
  producto_id: number
  cantidad: number | string
  precio_unitario: number | string
  subtotal?: number | string
}

/** @deprecated Mantener para cotizaciones existentes */
export interface CotizacionCompra extends Auditoria {
  id: number
  codigo: string
  proveedor_id: number
  estado: string
  fecha?: string | null
  observaciones?: string | null
  total: number | string
  detalles: DetalleCompra[]
}

/** @deprecated Mantener para cotizaciones existentes */
export interface CotizacionCompraCreate {
  proveedor_id: number
  estado?: string
  fecha?: string | null
  observaciones?: string | null
  detalles: DetalleCompra[]
}

export const ESTADO_COMPRA_COLORS: Record<string, string> = {
  BORRADOR: 'grey',
  PENDIENTE: 'warning',
  APROBADA: 'info',
  CONFIRMADA: 'success',
  RECHAZADA: 'error',
  RECIBIDA: 'success',
  CANCELADA: 'error',
}
