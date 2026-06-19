export interface Compania {
  id: number
  codigo: string
  nombre: string
  nit?: string | null
  direccion?: string | null
  telefono?: string | null
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface Sucursal {
  id: number
  codigo: string
  nombre: string
  compania_id: number
  ciudad_id: number
  direccion?: string | null
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export type CompaniaCreate = Pick<Compania, 'codigo' | 'nombre' | 'nit' | 'direccion' | 'telefono' | 'activo'>
export type SucursalCreate = Pick<Sucursal, 'codigo' | 'nombre' | 'compania_id' | 'ciudad_id' | 'direccion' | 'activo'>
