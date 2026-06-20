import { api } from './api'
import type {
  Proveedor,
  ProveedorCreate,
  CotizacionCompra,
  CotizacionCompraCreate,
  OrdenCompra,
  OrdenCompraCreate,
  RecepcionCompra,
  RecepcionCompraCreate,
} from '@/types/compras.types'

export const comprasService = {
  getProveedores() {
    return api.get<Proveedor[]>('/compras/proveedores')
  },
  getProveedor(id: number) {
    return api.get<Proveedor>(`/compras/proveedores/${id}`)
  },
  createProveedor(data: ProveedorCreate) {
    return api.post<Proveedor>('/compras/proveedores', data)
  },
  updateProveedor(id: number, data: Partial<ProveedorCreate>) {
    return api.put<Proveedor>(`/compras/proveedores/${id}`, data)
  },
  deleteProveedor(id: number) {
    return api.delete(`/compras/proveedores/${id}`)
  },

  getCotizaciones() {
    return api.get<CotizacionCompra[]>('/compras/cotizaciones')
  },
  createCotizacion(data: CotizacionCompraCreate) {
    return api.post<CotizacionCompra>('/compras/cotizaciones', data)
  },
  updateCotizacion(id: number, data: Partial<CotizacionCompraCreate>) {
    return api.put<CotizacionCompra>(`/compras/cotizaciones/${id}`, data)
  },
  deleteCotizacion(id: number) {
    return api.delete(`/compras/cotizaciones/${id}`)
  },

  getOrdenesCompra() {
    return api.get<OrdenCompra[]>('/compras/ordenes-compra')
  },
  getOrdenCompra(id: number) {
    return api.get<OrdenCompra>(`/compras/ordenes-compra/${id}`)
  },
  createOrdenCompra(data: OrdenCompraCreate) {
    return api.post<OrdenCompra>('/compras/ordenes-compra', data)
  },
  updateOrdenCompra(id: number, data: Partial<OrdenCompraCreate>) {
    return api.put<OrdenCompra>(`/compras/ordenes-compra/${id}`, data)
  },
  deleteOrdenCompra(id: number) {
    return api.delete(`/compras/ordenes-compra/${id}`)
  },
  aprobarOrdenCompra(id: number) {
    return api.post<OrdenCompra>(`/compras/ordenes-compra/${id}/aprobar`)
  },
  cancelarOrdenCompra(id: number) {
    return api.post<OrdenCompra>(`/compras/ordenes-compra/${id}/cancelar`)
  },

  /** Alias lectura legacy */
  getOrdenes() {
    return api.get<OrdenCompra[]>('/compras/ordenes')
  },

  getRecepcionesCompra() {
    return api.get<RecepcionCompra[]>('/compras/recepciones-compra')
  },
  getRecepcionCompra(id: number) {
    return api.get<RecepcionCompra>(`/compras/recepciones-compra/${id}`)
  },
  createRecepcionCompra(data: RecepcionCompraCreate) {
    return api.post<RecepcionCompra>('/compras/recepciones-compra', data)
  },
  updateRecepcionCompra(id: number, data: Partial<RecepcionCompraCreate>) {
    return api.put<RecepcionCompra>(`/compras/recepciones-compra/${id}`, data)
  },
  deleteRecepcionCompra(id: number) {
    return api.delete(`/compras/recepciones-compra/${id}`)
  },
  confirmarRecepcionCompra(id: number) {
    return api.post<RecepcionCompra>(`/compras/recepciones-compra/${id}/confirmar`)
  },
  cancelarRecepcionCompra(id: number) {
    return api.post<RecepcionCompra>(`/compras/recepciones-compra/${id}/cancelar`)
  },

  /** Alias lectura legacy */
  getRecepciones() {
    return api.get<RecepcionCompra[]>('/compras/recepciones')
  },
}
