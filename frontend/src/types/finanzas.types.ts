export interface Auditoria {
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface CuentaPorCobrar extends Auditoria {
  id: number
  codigo: string
  referencia_tipo?: string | null
  referencia_id?: number | null
  tercero_id?: number | null
  tercero_tipo?: string | null
  monto: number | string
  saldo: number | string
  estado: string
  fecha_vencimiento?: string | null
  descripcion?: string | null
}

export interface CuentaPorPagar extends Auditoria {
  id: number
  codigo: string
  referencia_tipo?: string | null
  referencia_id?: number | null
  tercero_id?: number | null
  tercero_tipo?: string | null
  monto: number | string
  saldo: number | string
  estado: string
  fecha_vencimiento?: string | null
  descripcion?: string | null
}

export interface Cobro {
  id: number
  cuenta_cobrar_id: number
  monto: number | string
  metodo: string
  referencia?: string | null
  fecha?: string | null
}

export interface CobroCreate {
  cuenta_cobrar_id: number
  monto: number | string
  metodo?: string
  referencia?: string | null
  fecha?: string | null
}

export interface Pago {
  id: number
  cuenta_pagar_id: number
  monto: number | string
  metodo: string
  referencia?: string | null
  fecha?: string | null
}

export interface PagoCreate {
  cuenta_pagar_id: number
  monto: number | string
  metodo?: string
  referencia?: string | null
  fecha?: string | null
}

export interface Caja extends Auditoria {
  id: number
  codigo: string
  nombre: string
  saldo: number | string
}

export type CajaCreate = Omit<Caja, 'id' | 'creado_en' | 'actualizado_en' | 'saldo'> & { saldo?: number | string }

export interface Banco extends Auditoria {
  id: number
  codigo: string
  nombre: string
}

export type BancoCreate = Omit<Banco, 'id' | 'creado_en' | 'actualizado_en'>

export interface MovimientoCaja {
  id: number
  caja_id: number
  tipo: string
  monto: number | string
  referencia?: string | null
  observaciones?: string | null
}

export interface MovimientoBancario {
  id: number
  cuenta_bancaria_id: number
  tipo: string
  monto: number | string
  referencia?: string | null
  observaciones?: string | null
}

export const ESTADO_FINANZA_COLORS: Record<string, string> = {
  PENDIENTE: 'warning',
  PAGADO: 'success',
  PARCIAL: 'info',
  VENCIDO: 'error',
  ANULADO: 'grey',
}
