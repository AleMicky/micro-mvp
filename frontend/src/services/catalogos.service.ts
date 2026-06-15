import { api } from './api'
import type {
  Categoria,
  CategoriaCreate,
  CategoriaUpdate,
  Marca,
  MarcaCreate,
  MarcaUpdate,
  Producto,
  ProductoCreate,
  ProductoUpdate,
  UnidadMedida,
  UnidadMedidaCreate,
  UnidadMedidaUpdate,
} from '@/types/catalogos.types'

export const catalogosService = {
  getCategorias() {
    return api.get<Categoria[]>('/catalogos/categorias')
  },
  createCategoria(data: CategoriaCreate) {
    return api.post<Categoria>('/catalogos/categorias', data)
  },
  updateCategoria(id: number, data: CategoriaUpdate) {
    return api.put<Categoria>(`/catalogos/categorias/${id}`, data)
  },
  deleteCategoria(id: number) {
    return api.delete(`/catalogos/categorias/${id}`)
  },

  getMarcas() {
    return api.get<Marca[]>('/catalogos/marcas')
  },
  createMarca(data: MarcaCreate) {
    return api.post<Marca>('/catalogos/marcas', data)
  },
  updateMarca(id: number, data: MarcaUpdate) {
    return api.put<Marca>(`/catalogos/marcas/${id}`, data)
  },
  deleteMarca(id: number) {
    return api.delete(`/catalogos/marcas/${id}`)
  },

  getUnidadesMedida() {
    return api.get<UnidadMedida[]>('/catalogos/unidades-medida')
  },
  createUnidadMedida(data: UnidadMedidaCreate) {
    return api.post<UnidadMedida>('/catalogos/unidades-medida', data)
  },
  updateUnidadMedida(id: number, data: UnidadMedidaUpdate) {
    return api.put<UnidadMedida>(`/catalogos/unidades-medida/${id}`, data)
  },
  deleteUnidadMedida(id: number) {
    return api.delete(`/catalogos/unidades-medida/${id}`)
  },

  getProductos() {
    return api.get<Producto[]>('/catalogos/productos')
  },
  createProducto(data: ProductoCreate) {
    return api.post<Producto>('/catalogos/productos', data)
  },
  updateProducto(id: number, data: ProductoUpdate) {
    return api.put<Producto>(`/catalogos/productos/${id}`, data)
  },
  deleteProducto(id: number) {
    return api.delete(`/catalogos/productos/${id}`)
  },
}
