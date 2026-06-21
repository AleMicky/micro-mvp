export interface Auditoria {
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface Cliente extends Auditoria {
  id: number
  codigo: string
  nombre: string
  rfc?: string | null
  email?: string | null
  telefono?: string | null
  direccion?: string | null
}

export type ClienteCreate = Omit<Cliente, 'id' | 'creado_en' | 'actualizado_en'>

export interface DetalleVenta {
  id?: number
  producto_id: number | null
  cantidad: number | string
  precio_unitario: number | string
  subtotal?: number | string
}

export interface CotizacionVenta extends Auditoria {
  id: number
  codigo: string
  cliente_id: number
  estado: string
  fecha?: string | null
  observaciones?: string | null
  total: number | string
  detalles: DetalleVenta[]
}

export interface CotizacionVentaCreate {
  cliente_id: number
  estado?: string
  fecha?: string | null
  observaciones?: string | null
  detalles: DetalleVenta[]
}

export interface Venta extends Auditoria {
  id: number
  codigo: string
  cliente_id: number
  cotizacion_id?: number | null
  almacen_id: number
  estado: string
  fecha?: string | null
  observaciones?: string | null
  total: number | string
  detalles: DetalleVenta[]
}

export interface VentaCreate {
  cliente_id: number
  cotizacion_id?: number | null
  almacen_id: number
  estado?: string
  fecha?: string | null
  observaciones?: string | null
  detalles: DetalleVenta[]
}

export interface Factura extends Auditoria {
  id: number
  codigo: string
  venta_id: number
  estado: string
  fecha?: string | null
  subtotal: number | string
  impuesto: number | string
  total: number | string
  detalles: DetalleVenta[]
}

export interface FacturaCreate {
  venta_id: number
  fecha?: string | null
  impuesto?: number | string
}

export const ESTADO_VENTA_COLORS: Record<string, string> = {
  BORRADOR: 'grey',
  PENDIENTE: 'warning',
  CONFIRMADA: 'info',
  FACTURADA: 'success',
  CANCELADA: 'error',
}
