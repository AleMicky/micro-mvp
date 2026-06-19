export interface Auditoria {
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface Categoria {
  id: number
  codigo: string
  nombre: string
  descripcion: string | null
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface CategoriaCreate {
  codigo: string
  nombre: string
  descripcion?: string | null
  activo?: boolean
}

export interface CategoriaUpdate {
  codigo?: string
  nombre?: string
  descripcion?: string | null
  activo?: boolean
}

export interface Marca {
  id: number
  codigo: string
  nombre: string
  descripcion: string | null
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface MarcaCreate {
  codigo: string
  nombre: string
  descripcion?: string | null
  activo?: boolean
}

export interface MarcaUpdate {
  codigo?: string
  nombre?: string
  descripcion?: string | null
  activo?: boolean
}

export interface UnidadMedida {
  id: number
  codigo: string
  nombre: string
  abreviatura: string
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface UnidadMedidaCreate {
  codigo: string
  nombre: string
  abreviatura: string
  activo?: boolean
}

export interface UnidadMedidaUpdate {
  codigo?: string
  nombre?: string
  abreviatura?: string
  activo?: boolean
}

export interface Producto {
  id: number
  codigo: string
  codigo_barras?: string
  nombre: string
  descripcion: string | null
  categoria_id: number
  marca_id: number | null
  unidad_medida_id: number
  imagen_url?: string
  precio_actual?: number
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface ProductoCreate {
  codigo: string
  codigo_barras?: string
  nombre: string
  descripcion?: string | null
  categoria_id: number
  marca_id?: number | null
  unidad_medida_id: number
  precio_venta?: number
  activo?: boolean
}

export interface ProductoUpdate {
  codigo?: string
  codigo_barras?: string
  nombre?: string
  descripcion?: string | null
  categoria_id?: number
  marca_id?: number | null
  unidad_medida_id?: number
  activo?: boolean
}

export interface PrecioProducto {
  id: number
  producto_id: number
  precio_venta: number
  fecha_inicio: string
  fecha_fin: string | null
  activo: boolean
  creado_en?: string
  actualizado_en?: string
}

export interface PrecioProductoCreate {
  precio_venta: number
}
