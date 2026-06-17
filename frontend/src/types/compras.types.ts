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

export interface DetalleCompra {
  id?: number
  producto_id: number
  cantidad: number | string
  precio_unitario: number | string
  subtotal?: number | string
}

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

export interface CotizacionCompraCreate {
  proveedor_id: number
  estado?: string
  fecha?: string | null
  observaciones?: string | null
  detalles: DetalleCompra[]
}

export interface OrdenCompra extends Auditoria {
  id: number
  codigo: string
  proveedor_id: number
  cotizacion_id?: number | null
  estado: string
  fecha?: string | null
  observaciones?: string | null
  total: number | string
  detalles: DetalleCompra[]
}

export interface OrdenCompraCreate {
  proveedor_id: number
  cotizacion_id?: number | null
  estado?: string
  fecha?: string | null
  observaciones?: string | null
  detalles: DetalleCompra[]
}

export interface RecepcionCompra extends Auditoria {
  id: number
  codigo: string
  orden_id: number
  almacen_id: number
  estado: string
  fecha?: string | null
  observaciones?: string | null
  detalles: { id: number; producto_id: number; cantidad: number | string }[]
}

export interface RecepcionCompraCreate {
  orden_id: number
  almacen_id: number
  fecha?: string | null
  observaciones?: string | null
  detalles: { producto_id: number; cantidad: number | string }[]
}

export const ESTADO_COMPRA_COLORS: Record<string, string> = {
  BORRADOR: 'grey',
  PENDIENTE: 'warning',
  APROBADA: 'info',
  RECHAZADA: 'error',
  RECIBIDA: 'success',
  CANCELADA: 'error',
}
