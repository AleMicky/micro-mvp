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
  getOrdenes() {
    return api.get<OrdenCompra[]>('/compras/ordenes')
  },
  createOrden(data: OrdenCompraCreate) {
    return api.post<OrdenCompra>('/compras/ordenes', data)
  },
  updateOrden(id: number, data: Partial<OrdenCompraCreate>) {
    return api.put<OrdenCompra>(`/compras/ordenes/${id}`, data)
  },
  deleteOrden(id: number) {
    return api.delete(`/compras/ordenes/${id}`)
  },
  aprobarOrden(id: number) {
    return api.post<OrdenCompra>(`/compras/ordenes/${id}/aprobar`)
  },
  getRecepciones() {
    return api.get<RecepcionCompra[]>('/compras/recepciones')
  },
  createRecepcion(data: RecepcionCompraCreate) {
    return api.post<RecepcionCompra>('/compras/recepciones', data)
  },
}
