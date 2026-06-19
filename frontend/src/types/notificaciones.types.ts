export interface Notificacion {
  id: number
  cliente_id?: number | null
  tipo: string
  contenido: string
  evento_origen: string
  creado_en: string
}
