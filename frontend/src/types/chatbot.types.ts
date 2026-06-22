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

export interface Etiqueta {
  id: number
  nombre: string
  color: string
  creado_en: string
}

export interface EtiquetaCreate {
  nombre: string
  color: string
}

export interface EtiquetaUpdate {
  nombre?: string
  color?: string
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
  etiquetas: Etiqueta[]
}

export interface Mensaje {
  id: number
  direccion: 'entrante' | 'saliente'
  origen: 'cliente' | 'bot' | 'agente'
  texto: string
  tipo_mensaje: 'texto' | 'imagen' | 'documento'
  nombre_archivo: string | null
  wa_message_id: string | null
  creado_en: string
}

export interface ResponderRequest {
  texto: string
}

export interface TunnelUrl {
  url: string | null
  activo: boolean
}
