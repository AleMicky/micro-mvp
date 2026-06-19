import { api } from './api'
import type { Compania, CompaniaCreate, Sucursal, SucursalCreate } from '@/types/company.types'

export const companyService = {
  getCompanias() {
    return api.get<Compania[]>('/companias')
  },
  getCompania(id: number) {
    return api.get<Compania>(`/companias/${id}`)
  },
  createCompania(data: CompaniaCreate) {
    return api.post<Compania>('/companias', data)
  },
  updateCompania(id: number, data: Partial<CompaniaCreate>) {
    return api.put<Compania>(`/companias/${id}`, data)
  },
  deleteCompania(id: number) {
    return api.delete(`/companias/${id}`)
  },
  getSucursales() {
    return api.get<Sucursal[]>('/sucursales')
  },
  getSucursalesByCompania(companiaId: number) {
    return api.get<Sucursal[]>(`/companias/${companiaId}/sucursales`)
  },
  createSucursal(data: SucursalCreate) {
    return api.post<Sucursal>('/sucursales', data)
  },
  updateSucursal(id: number, data: Partial<SucursalCreate>) {
    return api.put<Sucursal>(`/sucursales/${id}`, data)
  },
  deleteSucursal(id: number) {
    return api.delete(`/sucursales/${id}`)
  },
}
