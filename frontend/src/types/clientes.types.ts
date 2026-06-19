export interface Cliente {
  id: number
  codigo: string
  nombre: string
  email?: string | null
  telefono?: string | null
  documento?: string | null
  direccion?: string | null
  activo: boolean
  creado_en: string
  actualizado_en: string
  total_puntos?: number
}

export interface HistorialCliente {
  id: number
  cliente_id: number
  tipo: string
  descripcion?: string | null
  monto?: number | null
  referencia?: string | null
  creado_en: string
}

export interface PuntosCliente {
  id: number
  cliente_id: number
  puntos: number
  motivo?: string | null
  referencia?: string | null
  creado_en: string
}

export type ClienteCreate = Pick<Cliente, 'codigo' | 'nombre' | 'email' | 'telefono' | 'documento' | 'direccion' | 'activo'>
