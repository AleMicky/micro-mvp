import { api } from './api'
import type { Cliente, ClienteCreate, HistorialCliente, PuntosCliente } from '@/types/clientes.types'

export const clientesService = {
  getClientes() {
    return api.get<Cliente[]>('/clientes')
  },
  getCliente(id: number) {
    return api.get<Cliente>(`/clientes/${id}`)
  },
  createCliente(data: ClienteCreate) {
    return api.post<Cliente>('/clientes', data)
  },
  updateCliente(id: number, data: Partial<ClienteCreate>) {
    return api.put<Cliente>(`/clientes/${id}`, data)
  },
  getHistorial(clienteId: number) {
    return api.get<HistorialCliente[]>(`/clientes/${clienteId}/historial`)
  },
  asignarPuntos(clienteId: number, puntos: number, motivo?: string, referencia?: string) {
    return api.post<PuntosCliente>(`/clientes/${clienteId}/puntos`, { puntos, motivo, referencia })
  },
}
