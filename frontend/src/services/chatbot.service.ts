import { api } from './api'
import type {
  Conversacion,
  Etiqueta,
  EtiquetaCreate,
  EtiquetaUpdate,
  Mensaje,
  MensajeRequest,
  MensajeResponse,
  ResponderRequest,
  TunnelUrl,
} from '@/types/chatbot.types'

export const chatbotService = {
  enviarMensaje(payload: MensajeRequest) {
    return api.post<MensajeResponse>('/chatbot/mensaje', payload)
  },
  listarConversaciones() {
    return api.get<Conversacion[]>('/chatbot/conversaciones')
  },
  obtenerMensajes(conversacionId: number) {
    return api.get<Mensaje[]>(`/chatbot/conversaciones/${conversacionId}/mensajes`)
  },
  responderConversacion(conversacionId: number, payload: ResponderRequest) {
    return api.post<Mensaje>(`/chatbot/conversaciones/${conversacionId}/responder`, payload)
  },
  responderConversacionConAdjunto(conversacionId: number, archivo: File, caption?: string) {
    const formData = new FormData()
    formData.append('archivo', archivo)
    if (caption?.trim()) {
      formData.append('caption', caption.trim())
    }
    return api.post<Mensaje>(`/chatbot/conversaciones/${conversacionId}/responder-adjunto`, formData, {
      headers: { 'Content-Type': undefined as never },
    })
  },
  obtenerTunnelUrl() {
    return api.get<TunnelUrl>('/chatbot/tunnel-url')
  },

  getEtiquetas() {
    return api.get<Etiqueta[]>('/chatbot/etiquetas')
  },
  createEtiqueta(data: EtiquetaCreate) {
    return api.post<Etiqueta>('/chatbot/etiquetas', data)
  },
  updateEtiqueta(id: number, data: EtiquetaUpdate) {
    return api.put<Etiqueta>(`/chatbot/etiquetas/${id}`, data)
  },
  deleteEtiqueta(id: number) {
    return api.delete(`/chatbot/etiquetas/${id}`)
  },
  asignarEtiqueta(conversacionId: number, etiquetaId: number) {
    return api.post(`/chatbot/conversaciones/${conversacionId}/etiquetas/${etiquetaId}`)
  },
  desasignarEtiqueta(conversacionId: number, etiquetaId: number) {
    return api.delete(`/chatbot/conversaciones/${conversacionId}/etiquetas/${etiquetaId}`)
  },
}
