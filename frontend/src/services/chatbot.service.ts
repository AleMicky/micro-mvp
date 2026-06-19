import { api } from './api'
import type { Conversacion, Mensaje, MensajeRequest, MensajeResponse } from '@/types/chatbot.types'

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
}
