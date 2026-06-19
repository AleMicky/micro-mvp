export interface MensajeRequest {
  sesion_id: string
  texto: string
}

export interface MensajeResponse {
  respuesta: string
  opciones: string[] | null
  estado: string
}

export interface ChatMessage {
  rol: 'usuario' | 'bot'
  texto: string
  opciones?: string[] | null
}

export interface Conversacion {
  id: number
  sesion_id: string
  canal: string
  estado: string
  actualizado_en: string
  ultimo_mensaje: string | null
  ultimo_mensaje_en: string | null
  ultima_direccion: 'entrante' | 'saliente' | null
}

export interface Mensaje {
  id: number
  direccion: 'entrante' | 'saliente'
  texto: string
  wa_message_id: string | null
  creado_en: string
}
