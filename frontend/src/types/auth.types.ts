export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginRequest {
  identificador: string
  password: string
}

export interface RefreshRequest {
  refresh_token: string
}

export interface LogoutRequest {
  refresh_token: string
}

export interface MeResponse {
  id: number
  nombre_completo: string
  nombre_usuario: string
  correo: string
  activo: boolean
  ultimo_login_en: string | null
  roles: string[]
  permisos: string[]
  creado_en: string
  actualizado_en: string
}

export interface RolResumen {
  id: number
  codigo: string
  nombre: string
}

export interface Usuario {
  id: number
  nombre_completo: string
  nombre_usuario: string
  correo: string
  activo: boolean
  ultimo_login_en: string | null
  roles: RolResumen[]
  creado_en: string
  actualizado_en: string
}

export interface PermisoResumen {
  id: number
  codigo: string
  nombre: string
  modulo: string
}

export interface Rol {
  id: number
  codigo: string
  nombre: string
  descripcion: string | null
  activo: boolean
  permisos: PermisoResumen[]
  creado_en: string
  actualizado_en: string
}

export interface Permiso {
  id: number
  codigo: string
  nombre: string
  modulo: string
  descripcion: string | null
  activo: boolean
  creado_en: string
  actualizado_en: string
}

export interface ApiError {
  detail?: string | { msg: string }[]
  message?: string
}
