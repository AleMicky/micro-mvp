import { api } from './api'
import type { Notificacion } from '@/types/notificaciones.types'

export const notificacionesService = {
  getNotificaciones() {
    return api.get<Notificacion[]>('/notificaciones')
  },
  getByCliente(clienteId: number) {
    return api.get<Notificacion[]>(`/notificaciones/cliente/${clienteId}`)
  },
}
