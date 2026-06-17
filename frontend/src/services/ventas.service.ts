import { api } from './api'
import type {
  Cliente,
  ClienteCreate,
  CotizacionVenta,
  CotizacionVentaCreate,
  Venta,
  VentaCreate,
  Factura,
  FacturaCreate,
} from '@/types/ventas.types'

export const ventasService = {
  getClientes() {
    return api.get<Cliente[]>('/ventas/clientes')
  },
  createCliente(data: ClienteCreate) {
    return api.post<Cliente>('/ventas/clientes', data)
  },
  updateCliente(id: number, data: Partial<ClienteCreate>) {
    return api.put<Cliente>(`/ventas/clientes/${id}`, data)
  },
  deleteCliente(id: number) {
    return api.delete(`/ventas/clientes/${id}`)
  },
  getCotizaciones() {
    return api.get<CotizacionVenta[]>('/ventas/cotizaciones')
  },
  createCotizacion(data: CotizacionVentaCreate) {
    return api.post<CotizacionVenta>('/ventas/cotizaciones', data)
  },
  updateCotizacion(id: number, data: Partial<CotizacionVentaCreate>) {
    return api.put<CotizacionVenta>(`/ventas/cotizaciones/${id}`, data)
  },
  deleteCotizacion(id: number) {
    return api.delete(`/ventas/cotizaciones/${id}`)
  },
  getVentas() {
    return api.get<Venta[]>('/ventas/ventas')
  },
  createVenta(data: VentaCreate) {
    return api.post<Venta>('/ventas/ventas', data)
  },
  updateVenta(id: number, data: Partial<VentaCreate>) {
    return api.put<Venta>(`/ventas/ventas/${id}`, data)
  },
  deleteVenta(id: number) {
    return api.delete(`/ventas/ventas/${id}`)
  },
  confirmarVenta(id: number) {
    return api.post<Venta>(`/ventas/ventas/${id}/confirmar`)
  },
  getFacturas() {
    return api.get<Factura[]>('/ventas/facturas')
  },
  createFactura(data: FacturaCreate) {
    return api.post<Factura>('/ventas/facturas', data)
  },
}
