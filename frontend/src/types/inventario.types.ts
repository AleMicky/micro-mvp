export type TipoMovimiento =
  | 'INGRESO'
  | 'SALIDA'
  | 'AJUSTE_POSITIVO'
  | 'AJUSTE_NEGATIVO'
  | 'TRANSFERENCIA_SALIDA'
  | 'TRANSFERENCIA_ENTRADA'

export interface Almacen {
  id: number
  codigo: string
  nombre: string
  direccion: string | null
  sucursal_id?: number | null
  sucursal_codigo?: string | null
  sucursal_nombre?: string | null
  compania_id?: number | null
  compania_nombre?: string | null
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface AlmacenCreate {
  codigo: string
  nombre: string
  direccion?: string | null
  sucursal_id?: number | null
  activo?: boolean
}

export interface AlmacenUpdate {
  codigo?: string
  nombre?: string
  direccion?: string | null
  sucursal_id?: number | null
  activo?: boolean
}

export interface SucursalOption {
  id: number
  codigo: string
  nombre: string
  compania_id: number
  compania_nombre: string
}

export interface Existencia {
  id: number
  producto_id: number
  almacen_id: number
  cantidad_actual: number
  stock_minimo: number
  stock_maximo: number | null
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface MovimientoInventario {
  id: number
  tipo: TipoMovimiento
  producto_id: number
  almacen_id: number
  cantidad: number
  cantidad_anterior: number
  cantidad_nueva: number
  referencia_tipo: string | null
  referencia_id: number | null
  observaciones: string | null
  creado_en: string
}

export interface KardexResponse {
  producto_id: number
  total_movimientos: number
  movimientos: MovimientoInventario[]
}

export interface StockIngresoRequest {
  producto_id: number
  almacen_id: number
  cantidad: number
  observaciones?: string | null
  stock_minimo?: number | null
  stock_maximo?: number | null
}

export interface StockSalidaRequest {
  producto_id: number
  almacen_id: number
  cantidad: number
  observaciones?: string | null
}

export interface AjusteDetalleRequest {
  producto_id: number
  cantidad_nueva: number
}

export interface StockAjusteRequest {
  almacen_id: number
  motivo?: string | null
  observaciones?: string | null
  detalles: AjusteDetalleRequest[]
}

export interface TransferenciaDetalleRequest {
  producto_id: number
  cantidad: number
}

export interface StockTransferenciaRequest {
  almacen_origen_id: number
  almacen_destino_id: number
  observaciones?: string | null
  detalles: TransferenciaDetalleRequest[]
}

export interface StockOperacionResponse {
  existencia_id: number
  producto_id: number
  almacen_id: number
  cantidad_anterior: number
  cantidad_nueva: number
  movimiento: MovimientoInventario
}
